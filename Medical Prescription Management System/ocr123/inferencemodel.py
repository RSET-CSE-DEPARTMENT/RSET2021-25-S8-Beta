# import cv2
# import typing
# import numpy as np

# from mltu.inferenceModel import OnnxInferenceModel
# from mltu.utils.text_utils import ctc_decoder, get_cer, get_wer
# from mltu.transformers import ImageResizer

# class ImageToWordModel(OnnxInferenceModel):
#     def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.char_list = char_list

#     def predict(self, image: np.ndarray):
#         image = ImageResizer.resize_maintaining_aspect_ratio(image, *self.input_shapes[0][1:3][::-1])

#         image_pred = np.expand_dims(image, axis=0).astype(np.float32)

#         preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]

#         text = ctc_decoder(preds, self.char_list)[0]

#         return text

# if __name__ == "__main__":
#     import pandas as pd
#     from tqdm import tqdm
#     from mltu.configs import BaseModelConfigs

#     configs = BaseModelConfigs.load("Models/04_sentence_recognition/202301131202/configs.yaml")

#     model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

#     df = pd.read_csv("Models/04_sentence_recognition/202301131202/val.csv").values.tolist()

#     accum_cer, accum_wer = [], []
#     for image_path, label in tqdm(df):
#         image = cv2.imread(image_path.replace("\\", "/"))

#         prediction_text = model.predict(image)

#         cer = get_cer(prediction_text, label)
#         wer = get_wer(prediction_text, label)
#         print("Image: ", image_path)
#         print("Label:", label)
#         print("Prediction: ", prediction_text)
#         print(f"CER: {cer}; WER: {wer}")

#         accum_cer.append(cer)
#         accum_wer.append(wer)

#         cv2.imshow(prediction_text, image)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()

#     print(f"Average CER: {np.average(accum_cer)}, Average WER: {np.average(accum_wer)}")













import cv2
import os
import numpy as np
import typing
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder
from mltu.transformers import ImageResizer
from mltu.configs import BaseModelConfigs

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image: np.ndarray):
        if image is None:
            raise ValueError("Invalid image input: Image is None.")

        image = ImageResizer.resize_maintaining_aspect_ratio(image, *self.input_shapes[0][1:3][::-1])
        image_pred = np.expand_dims(image, axis=0).astype(np.float32)
        preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]
        text = ctc_decoder(preds, self.char_list)[0]
        return text

if __name__ == "__main__":
    configs = BaseModelConfigs.load(r"D:\xampp\htdocs\doctor_prescription\ocr\ocr\Models\04_sentence_recognition\202301131202\configs.yaml")
    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    image_path = r"media\input.png"  # Replace with the actual image path 

    # Check if the image file exists before reading
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}") 

    image = cv2.imread(image_path)
    
    # Ensure the image is loaded correctly
    if image is None:
        raise ValueError(f"Failed to load image. Please check the file format and path: {image_path}")

    prediction_text = model.predict(image)

    # print("Image: ", image_path)
    print("Prediction: ", prediction_text)

    # Store the prediction result in a text file
    with open("prediction_result.txt", "w", encoding="utf-8") as file:
        # file.write(f"Image: {image_path}\n")
        file.write(f" {prediction_text}\n")

    # print("Prediction saved to prediction_result.txt")

    # cv2.imshow(prediction_text, image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
