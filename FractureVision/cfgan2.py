import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from PIL import Image
import time
from pytorch_msssim import ssim
# ========== Generator ==========
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(2, 64, 4, 2, 1),
            nn.ReLU(True),
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(True)
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, 1, 4, 2, 1),
            nn.Tanh()
        )

    def forward(self, xray, ct):
        if self.training:
            ct = torch.nn.functional.dropout(ct, p=0.3)  # 🔥 Drop some CT info to force fusion
        x = torch.cat([xray, ct], dim=1)
        x = self.encoder(x)
        x = self.decoder(x)
        return x

# ========== Training Logic (Only Runs When Executed Directly) ==========
if __name__ == "__main__":
    def train_cfgan(plane, ct_root, xray_root, save_dir, resume=True):
        print(f"\n🔥 Training CFGAN for {plane.upper()}")

        ct_dir = os.path.join(ct_root, plane, 'train')
        xray_dir = os.path.join(xray_root, plane, 'train')
        save_path = os.path.join(save_dir, plane)
        os.makedirs(save_path, exist_ok=True)

        transform = transforms.Compose([
            transforms.Resize((256, 256)),  
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

        dataset = FusionDataset(xray_dir, ct_dir, transform)
        dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        gen = Generator().to(device)
        disc = Discriminator().to(device)

        bce = nn.BCELoss()
        l1 = nn.L1Loss()

        opt_gen = optim.Adam(gen.parameters(), lr=1e-4)
        opt_disc = optim.Adam(disc.parameters(), lr=1e-4)

        start_epoch = 0
        checkpoint_files = [f for f in os.listdir(save_path) if f.startswith('cfgan_epoch_') and f.endswith('.pth')]
        latest_checkpoint = None
        if checkpoint_files:
            checkpoint_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
            latest_checkpoint = os.path.join(save_path, checkpoint_files[-1])

        if resume and latest_checkpoint:
            checkpoint = torch.load(latest_checkpoint)
            gen.load_state_dict(checkpoint['gen_state_dict'])
            disc.load_state_dict(checkpoint['disc_state_dict'])
            opt_gen.load_state_dict(checkpoint['gen_opt_state_dict'])
            opt_disc.load_state_dict(checkpoint['disc_opt_state_dict'])
            start_epoch = checkpoint['epoch']
            print(f"\n⏪ Resumed from epoch {start_epoch}")
        else:
            print("\n🔄 No checkpoint found or resume=False. Starting fresh.")

        for epoch in range(start_epoch + 1, 26):
            for i, (xray, ct) in enumerate(dataloader):
                xray, ct = xray.to(device), ct.to(device)

                # === Train Discriminator ===
                fused = gen(xray, ct)
                real_label = torch.ones(xray.size(0), 1).to(device)
                fake_label = torch.zeros(xray.size(0), 1).to(device)

                real_out, fake_out = disc(xray, ct, fused.detach())

                d_loss_real = bce(real_out, real_label)
                d_loss_fake = bce(fake_out, fake_label)
                d_loss = (d_loss_real + d_loss_fake) / 2

                opt_disc.zero_grad()
                d_loss.backward()
                opt_disc.step()

                # === Train Generator ===
                fused = gen(xray, ct)
                fake_out, _ = disc(xray, ct, fused)
                gan_loss = bce(fake_out, real_label)

                fused_01 = (fused + 1) / 2
                ct_01 = (ct + 1) / 2
                xray_01 = (xray + 1) / 2

                l1_loss_val = l1(fused_01, ct_01)
                ssim_ct = ssim(fused_01, ct_01, data_range=1.0, size_average=True)
                ssim_xray = ssim(fused_01, xray_01, data_range=1.0, size_average=True)

                fusion_loss = 0.3 * l1_loss_val + 0.3 * (1 - ssim_ct) + 0.4 * (1 - ssim_xray)
                gen_loss = gan_loss + 100 * fusion_loss

                opt_gen.zero_grad()
                gen_loss.backward()
                opt_gen.step()

                if i % 10 == 0:
                    print(f"Epoch [{epoch}/25] Step [{i}/{len(dataloader)}] D Loss: {d_loss.item():.4f}, G Loss: {gen_loss.item():.4f}")

            if epoch % 5 == 0:
                torch.save({
                    'epoch': epoch,
                    'gen_state_dict': gen.state_dict(),
                    'disc_state_dict': disc.state_dict(),
                    'gen_opt_state_dict': opt_gen.state_dict(),
                    'disc_opt_state_dict': opt_disc.state_dict()
                }, os.path.join(save_path, f'cfgan_epoch_{epoch}.pth'))
                print(f"\n💾 Saved checkpoint at epoch {epoch}")

        print(f"✅ Training for {plane.upper()} complete!")

    # Training execution inside __main__
    planes = ['axial', 'coronal', 'sagittal']
    ct_base = r"C:\Peak_shit_project\cfgan\Ouput\CT_slices"
    xray_base = r"C:\Peak_shit_project\cfgan\Ouput\Pseudo_XRays"
    save_dir = r"saved_models_cfgan2"

    for plane in planes:
        train_cfgan(plane, ct_base, xray_base, save_dir, resume=True)
