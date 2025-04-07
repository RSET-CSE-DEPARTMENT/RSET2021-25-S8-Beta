package com.example.myapplication

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.border
import com.airbnb.lottie.compose.LottieAnimation
import com.airbnb.lottie.compose.LottieCompositionSpec
import com.airbnb.lottie.compose.rememberLottieComposition
import com.airbnb.lottie.compose.animateLottieCompositionAsState
import com.airbnb.lottie.compose.LottieConstants
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.sp
import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.myapplication.ui.theme.MyApplicationTheme
import com.example.myapplication.composables.CameraPreviewScreen
import com.example.myapplication.composables.FlashlightController
import com.example.myapplication.composables.TextToMorse
import com.example.myapplication.composables.ReferScreen
import com.example.myapplication.composables.QuizScreen
import com.example.myapplication.composables.TranslateScreen
import kotlinx.coroutines.*
import org.opencv.android.OpenCVLoader // Added import

class MainActivity : ComponentActivity() {

    private val cameraPermissionRequest =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
            if (isGranted) {
                Log.d("CameraPermission", "Permission granted")
                setCameraPreview()
            } else {
                Log.d("CameraPermission", "Permission denied")
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (OpenCVLoader.initLocal()) {
            Log.d("OpenCV", "OpenCV initialization succeeded")
        } else {
            Log.d("OpenCV", "OpenCV initialization failed")
        }

        setTheme(android.R.style.Theme_NoTitleBar_Fullscreen)
        setContent {
            var showSplashScreen by remember { mutableStateOf(true) }
            MyApplicationTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    if (showSplashScreen) {
                        MyLottieSplashScreen { showSplashScreen = false }
                    } else {
                        AppLayout(
                            onRequestPermission = { requestCameraPermission() }
                        )
                    }
                }
            }
        }
    }

    private fun requestCameraPermission() {
        Log.d("CameraPermission", "Checking for permission")
        when (ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.CAMERA
        )) {
            PackageManager.PERMISSION_GRANTED -> {
                Log.d("CameraPermission", "Permission already granted")
                setCameraPreview()
            }
            else -> {
                Log.d("CameraPermission", "Permission not granted, requesting")
                cameraPermissionRequest.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun setCameraPreview() {
        setContent {
            MyApplicationTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppLayout { requestCameraPermission() }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun AppLayout(onRequestPermission: () -> Unit) {
    val navController = rememberNavController()
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val screenWidthDp = LocalConfiguration.current.screenWidthDp.dp
    val drawerWidth = screenWidthDp * 2 / 3
    var isLearnExpanded by remember { mutableStateOf(false) }

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet(
                modifier = Modifier.width(drawerWidth),
                drawerContainerColor = Color(0xFF1A1A1A)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxHeight()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "Menu",
                        color = Color.White,
                        fontSize = 26.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    Divider(color = Color.Gray.copy(alpha = 0.3f))
                    Spacer(modifier = Modifier.height(16.dp))

                    NavigationDrawerItem(
                        label = { Text("Home", color = Color.White, fontSize = 18.sp) },
                        selected = navController.currentDestination?.route == "home",
                        onClick = {
                            scope.launch { drawerState.close() }
                            navController.navigate("home") {
                                popUpTo(navController.graph.startDestinationId)
                                launchSingleTop = true
                            }
                            isLearnExpanded = false
                        },
                        modifier = Modifier.padding(vertical = 4.dp)
                    )

                    Column {
                        NavigationDrawerItem(
                            label = { Text("Learn", color = Color.White, fontSize = 18.sp) },
                            selected = false,
                            onClick = {
                                isLearnExpanded = !isLearnExpanded
                            },
                            modifier = Modifier.padding(vertical = 4.dp)
                        )

                        AnimatedVisibility(
                            visible = isLearnExpanded,
                            enter = expandVertically() + fadeIn(),
                            exit = shrinkVertically() + fadeOut()
                        ) {
                            Column(modifier = Modifier.padding(start = 16.dp)) {
                                NavigationDrawerItem(
                                    label = { Text("Quiz", color = Color.White, fontSize = 16.sp) },
                                    selected = navController.currentDestination?.route == "quiz",
                                    onClick = {
                                        scope.launch { drawerState.close() }
                                        navController.navigate("quiz") {
                                            popUpTo(navController.graph.startDestinationId)
                                            launchSingleTop = true
                                        }
                                        isLearnExpanded = false
                                    },
                                    modifier = Modifier.padding(vertical = 2.dp)
                                )
                                NavigationDrawerItem(
                                    label = { Text("Refer", color = Color.White, fontSize = 16.sp) },
                                    selected = navController.currentDestination?.route == "refer",
                                    onClick = {
                                        scope.launch { drawerState.close() }
                                        navController.navigate("refer") {
                                            popUpTo(navController.graph.startDestinationId)
                                            launchSingleTop = true
                                        }
                                        isLearnExpanded = false
                                    },
                                    modifier = Modifier.padding(vertical = 2.dp)
                                )
                                NavigationDrawerItem(
                                    label = { Text("Translate", color = Color.White, fontSize = 16.sp) },
                                    selected = navController.currentDestination?.route == "translate",
                                    onClick = {
                                        scope.launch { drawerState.close() }
                                        navController.navigate("translate") {
                                            popUpTo(navController.graph.startDestinationId)
                                            launchSingleTop = true
                                        }
                                        isLearnExpanded = false
                                    },
                                    modifier = Modifier.padding(vertical = 2.dp)
                                )
                            }
                        }
                    }
                }
            }
        }
    ) {
        NavHost(navController = navController, startDestination = "home") {
            composable("home") {
                HomeScreen(
                    onRequestPermission = onRequestPermission,
                    onOpenDrawer = { scope.launch { drawerState.open() } }
                )
            }
            composable("refer") {
                ReferScreen(
                    onNavigateBack = { navController.popBackStack() },
                    onOpenDrawer = { scope.launch { drawerState.open() } }
                )
            }
            composable("quiz") {
                QuizScreen(
                    onNavigateBack = { navController.popBackStack() },
                    onOpenDrawer = { scope.launch { drawerState.open() } }
                )
            }
            composable("translate") {
                TranslateScreen(
                    onNavigateBack = { navController.popBackStack() },
                    onOpenDrawer = { scope.launch { drawerState.open() } }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun HomeScreen(
    onRequestPermission: () -> Unit,
    onOpenDrawer: () -> Unit
) {
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
                    "Morse Talk",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White,
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
                        Icons.Default.Menu,
                        contentDescription = "Menu",
                        tint = Color.White
                    )
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.Transparent
            )
        )

        var isCameraPreviewVisible by remember { mutableStateOf(false) }
        var text by remember { mutableStateOf("") }
        val context = LocalContext.current
        var messages by remember { mutableStateOf(listOf<Pair<String, String>>()) }
        val listState = rememberLazyListState()

        if (isCameraPreviewVisible) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(375.dp)
                    .padding(16.dp)
                    .border(0.dp, Color.Red.copy(alpha = 0.2f), RoundedCornerShape(12.dp))
            ) {
                Box(modifier = Modifier.fillMaxSize()) {
                    CameraPreviewScreen(
                        onCameraControlReady = { cameraControl ->
                            Log.d("HomeScreen", "CameraControl received: $cameraControl")
                        },
                        onMorseCodeDetected = { morseCode, decodedText ->
                            messages = messages + Pair(
                                "Received: $morseCode ($decodedText)",
                                getCurrentTimestamp()
                            )
                        }
                    )
                    Text(
                        text = "Receiving...",
                        color = Color.White.copy(alpha = 0.8f),
                        fontSize = 14.sp,
                        modifier = Modifier
                            .align(Alignment.TopStart)
                            .padding(8.dp)
                            .background(Color.Black.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
                            .padding(4.dp)
                    )
                }
            }
        }

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .padding(horizontal = 16.dp, vertical = 8.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF212121)),
            shape = RoundedCornerShape(12.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    reverseLayout = false,
                    state = listState
                ) {
                    items(messages) { messagePair ->
                        val (message, timestamp) = messagePair
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp)
                                .animateItemPlacement(),
                            horizontalArrangement = Arrangement.End
                        ) {
                            Card(
                                colors = CardDefaults.cardColors(containerColor = Color(0xFF4CAF50).copy(alpha = 0.8f)),
                                shape = RoundedCornerShape(12.dp),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Column(modifier = Modifier.padding(12.dp)) {
                                    Text(
                                        text = message,
                                        color = Color.White,
                                        fontSize = 16.sp
                                    )
                                    Text(
                                        text = timestamp,
                                        color = Color.White.copy(alpha = 0.7f),
                                        fontSize = 12.sp
                                    )
                                }
                            }
                        }
                    }
                }

                LaunchedEffect(messages) {
                    if (messages.isNotEmpty()) {
                        listState.animateScrollToItem(messages.size - 1)
                    }
                }

                Column(
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedTextField(
                        value = text,
                        onValueChange = { text = it },
                        label = { Text("Enter message", color = Color.White.copy(alpha = 0.7f)) },
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

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        EnhancedButton(
                            onClick = {
                                if (text.isNotEmpty()) {
                                    val textToMorse = TextToMorse()
                                    val isValidInput = text.uppercase().all { textToMorse.isSupportedChar(it) }

                                    if (isValidInput) {
                                        val flashlightController = FlashlightController(context)
                                        flashlightController.transmitMorseCode(text)
                                        messages = messages + Pair(text, getCurrentTimestamp())
                                        text = ""
                                    } else {
                                        Toast.makeText(context, "Input contains unsupported characters!", Toast.LENGTH_LONG).show()
                                    }

//                                    val morseCode = textToMorse.translateToMorse(text) // This line is now redundant
//                                    val flashlightController = FlashlightController(context)
//                                    flashlightController.transmitMorseCode(text) // Pass raw text directly
//                                    messages = messages + Pair(text, getCurrentTimestamp())
//                                    text = ""
                                }
                            },
                            text = "Transmit",
                            modifier = Modifier.weight(1f),
                            containerColor = Color(0xFF4CAF50)
                        )

                        EnhancedButton(
                            onClick = {
                                if (!isCameraPreviewVisible) {
                                    isCameraPreviewVisible = true
                                    onRequestPermission()
                                } else {
                                    isCameraPreviewVisible = false
                                }
                            },
                            text = if (isCameraPreviewVisible) "Receiving..." else "Receive",
                            isActive = isCameraPreviewVisible,
                            modifier = Modifier.weight(1f),
                            containerColor = if (isCameraPreviewVisible) Color(0xFFFFD700) else Color.White
                        )
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EnhancedButton(
    onClick: () -> Unit,
    text: String,
    isActive: Boolean = false,
    modifier: Modifier = Modifier,
    containerColor: Color = Color.White
) {
    Button(
        onClick = onClick,
        modifier = modifier
            .height(50.dp)
            .graphicsLayer {
                scaleX = if (isActive) 1.05f else 1f
                scaleY = if (isActive) 1.05f else 1f
            },
        colors = ButtonDefaults.buttonColors(containerColor = containerColor),
        shape = RoundedCornerShape(12.dp),
        elevation = ButtonDefaults.buttonElevation(
            defaultElevation = 4.dp,
            pressedElevation = 8.dp
        )
    ) {
        Text(
            text = text,
            color = if (isActive || containerColor == Color(0xFF4CAF50)) Color.White else Color.DarkGray,
            fontSize = 16.sp,
            fontWeight = FontWeight.Medium
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Preview(showBackground = true)
@Composable
fun HomeScreenPreview() {
    MyApplicationTheme {
        HomeScreen(
            onRequestPermission = {},
            onOpenDrawer = {}
        )
    }
}

@Composable
fun MyLottie() {
    val preLoaderLottie by rememberLottieComposition(
        LottieCompositionSpec.RawRes(R.raw.splash_animation)
    )

    val preLoaderProgress by animateLottieCompositionAsState(
        preLoaderLottie,
        isPlaying = true,
        iterations = LottieConstants.IterateForever,
        speed = 1.5f
    )

    LottieAnimation(
        composition = preLoaderLottie,
        progress = { preLoaderProgress.coerceIn(0f, 0.9f) },
        modifier = Modifier
            .fillMaxSize()
            .graphicsLayer(scaleX = 1.5f, scaleY = 1.5f, translationY = -300f)
    )
}

@Composable
fun MyLottieSplashScreen(onSplashComplete: () -> Unit) {
    val customFont = FontFamily(Font(R.font.del))

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Top
    ) {
        Spacer(modifier = Modifier.height(80.dp))
        Text(
            text = "Morse Talk",
            style = TextStyle(
                fontSize = 60.sp,
                fontFamily = customFont,
                fontWeight = FontWeight.Bold,
                brush = Brush.linearGradient(
                    colors = listOf(Color.Cyan, Color.Magenta)
                ),
                shadow = Shadow(
                    color = Color.Gray,
                    blurRadius = 4f
                )
            ),
            modifier = Modifier.padding(top = 90.dp, bottom = 2.dp)
        )

        MyLottie()
    }

    LaunchedEffect(Unit) {
        delay(2750)
        onSplashComplete()
    }
}

fun getCurrentTimestamp(): String {
    return java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault()).format(java.util.Date())
}