package com.example.myapplication.composables

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.tooling.preview.Preview
import com.example.myapplication.ui.theme.MyApplicationTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TranslateScreen(
    onNavigateBack: () -> Unit,
    onOpenDrawer: () -> Unit
) {
    var textInput by remember { mutableStateOf("") }
    var morseInput by remember { mutableStateOf("") }
    var isTextEditing by remember { mutableStateOf(false) } // Track which field is being edited
    var isMorseEditing by remember { mutableStateOf(false) }

    // Text-to-Morse converter
    val textToMorse = TextToMorse()

    // Morse-to-Text converter (inline for simplicity)
    val morseToTextMap = mapOf(
        ".-" to "A", "-..." to "B", "-.-." to "C", "-.." to "D", "." to "E",
        "..-." to "F", "--." to "G", "...." to "H", ".." to "I", ".---" to "J",
        "-.-" to "K", ".-.." to "L", "--" to "M", "-." to "N", "---" to "O",
        ".--." to "P", "--.-" to "Q", ".-." to "R", "..." to "S", "-" to "T",
        "..-" to "U", "...-" to "V", ".--" to "W", "-..-" to "X", "-.--" to "Y",
        "--.." to "Z", ".----" to "1", "..---" to "2", "...--" to "3",
        "....-" to "4", "....." to "5", "-...." to "6", "--..." to "7",
        "---.." to "8", "----." to "9", "-----" to "0", " " to " "
    )

    fun morseToText(morse: String): String {
        val words = morse.trim().split("\\s+".toRegex()) // Split by one or more spaces
        return words.map { morseToTextMap[it] ?: "?" }.joinToString("")
    }

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
                    "Translate",
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
                        imageVector = Icons.Default.Menu,
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
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Text Input Field
            OutlinedTextField(
                value = textInput,
                onValueChange = { newText ->
                    if (!isMorseEditing) { // Only update if not editing Morse field
                        textInput = newText.uppercase()
                        isTextEditing = true
                        morseInput = textToMorse.translateToMorse(newText)
                        isTextEditing = false
                    }
                },
                label = { Text("Enter text", color = Color.White.copy(alpha = 0.7f)) },
                modifier = Modifier.fillMaxWidth(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color(0xFF4CAF50),
                    unfocusedBorderColor = Color.Gray,
                    focusedLabelColor = Color.White,
                    cursorColor = Color(0xFF4CAF50),
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White.copy(alpha = 0.7f)
                ),
                shape = RoundedCornerShape(12.dp)
            )

            // Morse Input Field
            OutlinedTextField(
                value = morseInput,
                onValueChange = { newMorse ->
                    if (!isTextEditing) { // Only update if not editing Text field
                        morseInput = newMorse
                        isMorseEditing = true
                        textInput = morseToText(newMorse).uppercase()
                        isMorseEditing = false
                    }
                },
                label = { Text("Enter Morse code", color = Color.White.copy(alpha = 0.7f)) },
                modifier = Modifier.fillMaxWidth(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color(0xFF4CAF50),
                    unfocusedBorderColor = Color.Gray,
                    focusedLabelColor = Color.White,
                    cursorColor = Color(0xFF4CAF50),
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White.copy(alpha = 0.7f)
                ),
                shape = RoundedCornerShape(12.dp)
            )

            Button(
                onClick = onNavigateBack,
                colors = ButtonDefaults.buttonColors(containerColor = Color.Gray),
                shape = RoundedCornerShape(12.dp),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text(text = "Back to Home", color = Color.White, fontSize = 16.sp)
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun TranslateScreenPreview() {
    MyApplicationTheme {
        TranslateScreen(onNavigateBack = {}, onOpenDrawer = {})
    }
}