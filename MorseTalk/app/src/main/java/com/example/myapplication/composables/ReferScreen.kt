package com.example.myapplication.composables

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.myapplication.ui.theme.MyApplicationTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReferScreen(
    onNavigateBack: () -> Unit,
    onOpenDrawer: () -> Unit
) {
    val morseCodeMap = mapOf(
        "A" to ".-", "B" to "-...", "C" to "-.-.", "D" to "-..", "E" to ".",
        "F" to "..-.", "G" to "--.", "H" to "....", "I" to "..", "J" to ".---",
        "K" to "-.-", "L" to ".-..", "M" to "--", "N" to "-.", "O" to "---",
        "P" to ".--.", "Q" to "--.-", "R" to ".-.", "S" to "...", "T" to "-",
        "U" to "..-", "V" to "...-", "W" to ".--", "X" to "-..-", "Y" to "-.--",
        "Z" to "--.."
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(Color(0xFF2A2A2A), Color(0xFF1A1A1A))
                )
            )
            .systemBarsPadding()
    ) {
        TopAppBar(
            title = {
                Text(
                    "Learn Morse Code",
                    color = Color.White,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    style = TextStyle(
                        shadow = Shadow(
                            color = Color.Black.copy(alpha = 0.3f),
                            blurRadius = 2f
                        )
                    )
                )
            },
            navigationIcon = {
                IconButton(onClick = onOpenDrawer) {
                    Icon(
                        imageVector = androidx.compose.material.icons.Icons.Default.Menu,
                        contentDescription = "Menu",
                        tint = Color.White
                    )
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.Transparent
            )
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            ReferenceTable(morseCodeMap)

            Button(
                onClick = onNavigateBack,
                colors = ButtonDefaults.buttonColors(containerColor = Color.Gray),
                shape = RoundedCornerShape(12.dp),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp)
                    .height(50.dp)
            ) {
                Text(text = "Back to Home", color = Color.White, fontSize = 16.sp)
            }
        }
    }
}

@Composable
fun ReferenceTable(morseCodeMap: Map<String, String>) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .fillMaxHeight(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF212121)),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(morseCodeMap.entries.toList()) { entry ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color.Black.copy(alpha = 0.8f), RoundedCornerShape(8.dp))
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = entry.key,
                        color = Color.White,
                        fontSize = 18.sp
                    )
                    Text(
                        text = entry.value,
                        color = Color.White,
                        fontSize = 18.sp
                    )
                }
            }
        }
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
fun ReferScreenPreview() {
    MyApplicationTheme {
        ReferScreen(onNavigateBack = {}, onOpenDrawer = {})
    }
}