package com.example.myapplication.composables

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
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
import com.example.myapplication.ui.theme.MyApplicationTheme
import kotlin.random.Random
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QuizScreen(
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

    var currentQuestion by remember { mutableStateOf(generateQuestion(morseCodeMap)) }
    var score by remember { mutableIntStateOf(0) }
    var totalQuestions by remember { mutableIntStateOf(0) }
    var feedback by remember { mutableStateOf<String?>(null) }
    var answerSubmitted by remember { mutableStateOf(false) }

    LaunchedEffect(answerSubmitted) {
        if (answerSubmitted && feedback != null) {
            delay(2000)
            feedback = null
            currentQuestion = generateQuestion(morseCodeMap)
            answerSubmitted = false
        }
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
                    "Morse Code Quiz",
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
            QuizContent(
                question = currentQuestion,
                score = score,
                totalQuestions = totalQuestions,
                onAnswerSelected = { selectedLetter ->
                    totalQuestions++
                    feedback = if (selectedLetter == currentQuestion.correctLetter) {
                        score++
                        "Correct!"
                    } else {
                        "Wrong! Correct answer: ${currentQuestion.correctLetter}"
                    }
                    answerSubmitted = true
                },
                onResetQuiz = {
                    score = 0
                    totalQuestions = 0
                    feedback = null
                    currentQuestion = generateQuestion(morseCodeMap)
                }
            )

            feedback?.let {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = if (it.startsWith("Correct")) Color(0xFF4CAF50).copy(alpha = 0.2f) else Color(0xFFF44336).copy(alpha = 0.2f)
                    ),
                    shape = RoundedCornerShape(12.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Text(
                        text = it,
                        color = if (it.startsWith("Correct")) Color.Green else Color.Red,
                        fontSize = 18.sp,
                        modifier = Modifier.padding(12.dp),
                        textAlign = androidx.compose.ui.text.style.TextAlign.Center
                    )
                }
            }

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

// Rest of QuizScreen.kt (QuizQuestion, QuizContent, generateQuestion, Preview) remains unchanged...

data class QuizQuestion(
    val morseCode: String,
    val correctLetter: String,
    val options: List<String>
)

@Composable
fun QuizContent(
    question: QuizQuestion,
    score: Int,
    totalQuestions: Int,
    onAnswerSelected: (String) -> Unit,
    onResetQuiz: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .fillMaxHeight(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF212121)),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "What letter is this?",
                color = Color.White,
                fontSize = 20.sp
            )
            Text(
                text = question.morseCode,
                color = Color.White,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold
            )

            question.options.forEach { option ->
                Button(
                    onClick = { onAnswerSelected(option) },
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White),
                    shape = RoundedCornerShape(12.dp),
                    elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                ) {
                    Text(text = option, color = Color.DarkGray, fontSize = 16.sp)
                }
            }

            Text(
                text = "Score: $score / $totalQuestions",
                color = Color.White,
                fontSize = 18.sp
            )

            Button(
                onClick = onResetQuiz,
                colors = ButtonDefaults.buttonColors(containerColor = Color.Gray),
                shape = RoundedCornerShape(12.dp),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text(text = "Reset Quiz", color = Color.White, fontSize = 16.sp)
            }
        }
    }
}

private fun generateQuestion(morseCodeMap: Map<String, String>): QuizQuestion {
    val entries = morseCodeMap.entries.toList()
    val correctEntry = entries[Random.nextInt(entries.size)]
    val otherOptions = entries
        .filter { it != correctEntry }
        .shuffled()
        .take(3)
        .map { it.key }
    val options = (listOf(correctEntry.key) + otherOptions).shuffled()
    return QuizQuestion(
        morseCode = correctEntry.value,
        correctLetter = correctEntry.key,
        options = options
    )
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
fun QuizScreenPreview() {
    MyApplicationTheme {
        QuizScreen(onNavigateBack = {}, onOpenDrawer = {})
    }
}