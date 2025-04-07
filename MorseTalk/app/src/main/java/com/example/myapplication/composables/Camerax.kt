package com.example.myapplication.composables

import android.content.Context
import android.hardware.camera2.CaptureRequest
import android.util.Log
import androidx.annotation.OptIn
import androidx.camera.camera2.interop.Camera2CameraControl
import androidx.camera.camera2.interop.CaptureRequestOptions
import androidx.camera.camera2.interop.ExperimentalCamera2Interop
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import kotlinx.coroutines.*
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine
import kotlin.math.abs
import org.opencv.imgproc.Imgproc
import org.opencv.core.*

@OptIn(ExperimentalCamera2Interop::class)
@Composable
fun CameraPreviewScreen(
    onCameraControlReady: (CameraControl) -> Unit,
    onMorseCodeDetected: (String, String) -> Unit
) {
    val lensFacing = CameraSelector.LENS_FACING_BACK
    val lifecycleOwner = LocalLifecycleOwner.current
    val context = LocalContext.current
    val preview = Preview.Builder().build()
    val previewView = remember { PreviewView(context) }
    var cameraControl by remember { mutableStateOf<CameraControl?>(null) }

    var currentZoom by remember { mutableFloatStateOf(1.5f) }
    val maxZoom = 6f

    var roiX by remember { mutableFloatStateOf(0f) }
    var roiY by remember { mutableFloatStateOf(0f) }
    var roiSize by remember { mutableFloatStateOf(0f) }
    var roiSizeRatio by remember { mutableIntStateOf(2) }

    var brightness by remember { mutableDoubleStateOf(0.0) }
    var flashStartTime by remember { mutableStateOf<Long?>(null) }
    var flashEndTime by remember { mutableStateOf<Long?>(null) }
    var flashDurations by remember { mutableStateOf(listOf<Long>()) }
    var isFlashOn by remember { mutableStateOf(false) }
    var previousBrightness by remember { mutableDoubleStateOf(0.0) }

    var lastProcessedTime by remember { mutableStateOf(0L) }
    val morseCodeBuilder = remember { StringBuilder() }

    val morseToTextMap = mapOf(
        ".-" to "A", "-..." to "B", "-.-." to "C", "-.." to "D", "." to "E",
        "..-." to "F", "--." to "G", "...." to "H", ".." to "I", ".---" to "J",
        "-.-" to "K", ".-.." to "L", "--" to "M", "-." to "N", "---" to "O",
        ".--." to "P", "--.-" to "Q", ".-." to "R", "..." to "S", "-" to "T",
        "..-" to "U", "...-" to "V", ".--" to "W", "-..-" to "X", "-.--" to "Y",
        "--.." to "Z", ".----" to "1", "..---" to "2", "...--" to "3",
        "....-" to "4", "....." to "5", "-...." to "6", "--..." to "7",
        "---.." to "8", "----." to "9", "-----" to "0","..--" to " "
    )

    fun morseToText(morse: String): String {
        val words = morse.trim().split("\\s+".toRegex())
        return words.map { morseToTextMap[it] ?: "?" }.joinToString("")
    }

    LaunchedEffect(lensFacing) {
        val cameraProvider = context.getCameraProvider()
        cameraProvider.unbindAll()

        val imageAnalyzer = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also { analysis ->
                analysis.setAnalyzer(ContextCompat.getMainExecutor(context)) { imageProxy ->
                    CoroutineScope(Dispatchers.Default).launch {
                        val result = analyzeBrightness(imageProxy, roiSizeRatio)
                        brightness = result.brightness
                        roiX = result.roiX.toFloat()
                        roiY = result.roiY.toFloat()
                        roiSize = result.roiSize.toFloat()

                        if (previousBrightness == 0.0) {
                            previousBrightness = brightness
                        }

                        val temporalDelta = brightness - previousBrightness
                        previousBrightness = brightness

                        val deltaThreshold = 20.0
                        val currentTime = System.currentTimeMillis()

                        if (abs(temporalDelta) > deltaThreshold) {
                            if (temporalDelta > deltaThreshold && !isFlashOn) {
                                flashEndTime?.let { endTime ->
                                    val offDuration = currentTime - endTime
                                    if (offDuration > 200) {
                                        flashDurations = flashDurations + (-offDuration)
                                        Log.d("MorseDetect", "Off duration: $offDuration ms")
                                    }
                                }
                                flashStartTime = currentTime
                                isFlashOn = true
                                Log.d("MorseDetect", "Flash ON at $currentTime")
                            } else if (temporalDelta < -deltaThreshold && isFlashOn) {
                                flashStartTime?.let { startTime ->
                                    val onDuration = currentTime - startTime
                                    if (onDuration > 50) { // Filter out noise
                                        flashDurations = flashDurations + onDuration
                                        Log.d("MorseDetect", "Flash OFF, onDuration: $onDuration ms")
                                    }
                                }
                                flashEndTime = currentTime
                                isFlashOn = false
                            }
                            // Update lastProcessedTime after each flash event
                            lastProcessedTime = currentTime
                        }

                        val timeSinceLastProcess = currentTime - lastProcessedTime
                        val lastDuration = flashDurations.lastOrNull()
                        val hasLetterGap = lastDuration?.let { it < -1000 && it > -1400 } ?: false // 1000–1400ms letter gap
                        val hasWordGap = lastDuration?.let { it < -1400 } ?: false // >1400ms word gap

                        if (flashDurations.isNotEmpty() && (hasLetterGap || hasWordGap || timeSinceLastProcess > 3000)) {
                            val morseSegment = decodeFlashDurations(flashDurations)
                            if (morseSegment.isNotEmpty()) {
                                // Append segment with a space after each letter
                                if (morseCodeBuilder.isNotEmpty()) {
                                    if (hasWordGap) {
                                        morseCodeBuilder.append("  ") // Word gap
                                    } else if (hasLetterGap || timeSinceLastProcess > 3000) {
                                        morseCodeBuilder.append(" ") // Letter gap or timeout
                                    }
                                }
                                morseCodeBuilder.append(morseSegment)
                                // Add a space after the segment if it’s a letter
                                if (!hasWordGap) {
                                    morseCodeBuilder.append(" ")
                                }
                                Log.d("MorseDetect", "Segment decoded: $morseSegment, Morse so far: ${morseCodeBuilder.toString()}")

                                // Send updated message
                                val fullMorseCode = morseCodeBuilder.toString().trim()
                                val decodedText = morseToText(fullMorseCode)
                                onMorseCodeDetected(fullMorseCode, decodedText)
                                Log.d("MorseDetect", "Current decode: $fullMorseCode -> $decodedText")

                                // Clear durations after each segment
                                flashDurations = emptyList()
                                lastProcessedTime = currentTime

                                // Reset only on word gap
                                if (hasWordGap) {
                                    morseCodeBuilder.clear()
                                    Log.d("MorseDetect", "Word gap detected, resetting builder")
                                }
                            } else {
                                flashDurations = emptyList()
                                lastProcessedTime = currentTime
                            }
                        }

                        // Hard reset after long inactivity
                        if (timeSinceLastProcess > 5000 && morseCodeBuilder.isNotEmpty()) {
                            val fullMorseCode = morseCodeBuilder.toString().trim()
                            val decodedText = morseToText(fullMorseCode)
                            onMorseCodeDetected(fullMorseCode, decodedText)
                            Log.d("MorseDetect", "Inactivity timeout: $fullMorseCode -> $decodedText")
                            morseCodeBuilder.clear()
                            flashDurations = emptyList()
                            lastProcessedTime = currentTime
                        }

                        imageProxy.close()
                    }
                }
            }

        val camera = cameraProvider.bindToLifecycle(
            lifecycleOwner,
            CameraSelector.Builder().requireLensFacing(lensFacing).build(),
            preview,
            imageAnalyzer
        )

        cameraControl = camera.cameraControl
        cameraControl?.setZoomRatio(currentZoom)
        preview.setSurfaceProvider(previewView.surfaceProvider)
        cameraControl?.let(onCameraControlReady)

        val camera2Control = Camera2CameraControl.from(cameraControl!!)
        val captureRequestOptions = CaptureRequestOptions.Builder()
            .setCaptureRequestOption(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_OFF)
            .setCaptureRequestOption(CaptureRequest.SENSOR_SENSITIVITY, 200)
            .setCaptureRequestOption(CaptureRequest.SENSOR_EXPOSURE_TIME, 100000000L)
            .setCaptureRequestOption(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF)
            .setCaptureRequestOption(CaptureRequest.CONTROL_AE_LOCK, true)
            .build()

        camera2Control.captureRequestOptions = captureRequestOptions
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTransformGestures { _, _, zoomChange, _ ->
                    val newZoom = (currentZoom * zoomChange).coerceIn(1f, maxZoom)
                    if (newZoom != currentZoom) {
                        currentZoom = newZoom
                        cameraControl?.setZoomRatio(newZoom)
                    }
                }
            }
    ) {
        AndroidView(factory = { previewView }, modifier = Modifier.matchParentSize())

        Canvas(modifier = Modifier.matchParentSize()) {
            drawRect(
                color = Color.Red,
                topLeft = Offset(roiX, roiY),
                size = Size(roiSize, roiSize),
                style = Stroke(width = 3.dp.toPx())
            )
        }
    }

    Column {
        Text(
            text = if (isFlashOn) "Flash Detected!" else "No Flash Detected",
            color = Color.White
        )
        Text("Brightness: $brightness")
        Column(modifier = Modifier.padding(8.dp)) {
            Text(text = "Flash Durations (ms):", color = Color.White)
            flashDurations.forEach { duration ->
                Text(text = "$duration ms", color = Color.White)
            }
            Text(text = "Decoded Morse: ${morseCodeBuilder.toString()}", color = Color.White)
        }
    }
}

private fun decodeFlashDurations(durations: List<Long>): String {
    val morseCode = StringBuilder()
    var i = 0
    while (i < durations.size) {
        val duration = durations[i]
        if (duration > 0) { // Flash on
            if (duration < 350) {
                morseCode.append(".")
                Log.d("MorseDetect", "Dot detected: $duration ms")
            } else {
                morseCode.append("-")
                Log.d("MorseDetect", "Dash detected: $duration ms")
            }
        } else { // Flash off
            val gap = -duration
            if (gap > 1400) { // Word gap
                morseCode.append("  ")
                Log.d("MorseDetect", "Word gap detected: $gap ms")
            } else if (gap > 1000) { // Letter gap
                morseCode.append(" ")
                Log.d("MorseDetect", "Letter gap detected: $gap ms")
            } else {
                Log.d("MorseDetect", "Intra-letter gap ignored: $gap ms")
            }
        }
        i++
    }
    return morseCode.toString().trim()
}

data class BrightnessResult(val brightness: Double, val roiX: Int, val roiY: Int, val roiSize: Int)

private fun analyzeBrightness(imageProxy: ImageProxy, roiSizeRatio: Int): BrightnessResult {
    return try {
        val buffer = imageProxy.planes[0].buffer
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)
        val width = imageProxy.width
        val height = imageProxy.height

        val mat = Mat(height, width, CvType.CV_8UC1)
        mat.put(0, 0, bytes)

        val grayMat = Mat()
        Imgproc.cvtColor(mat, grayMat, Imgproc.COLOR_YUV2GRAY_420)

        val clahe = Imgproc.createCLAHE(3.0)
        val enhancedMat = Mat()
        clahe.apply(grayMat, enhancedMat)

        Imgproc.GaussianBlur(enhancedMat, enhancedMat, Size(5.0, 5.0), 0.0)

        val roiSize = minOf(width, height) / roiSizeRatio
        val roiX = (width - roiSize) / 2
        val roiY = (height - roiSize) / 2

        if (roiX < 0 || roiY < 0 || roiX + roiSize > enhancedMat.cols() || roiY + roiSize > enhancedMat.rows()) {
            val brightness = Core.mean(enhancedMat).`val`[0]
            enhancedMat.release()
            grayMat.release()
            mat.release()
            return BrightnessResult(brightness, roiX, roiY, roiSize)
        }

        val roi = enhancedMat.submat(Rect(roiX, roiY, roiSize, roiSize))
        val brightness = Core.mean(roi).`val`[0]

        val minMax = Core.minMaxLoc(roi)
        val maxBrightness = minMax.maxVal

        val roiPixels = ByteArray(roi.total().toInt())
        roi.get(0, 0, roiPixels)

        val minBrightnessThreshold = maxBrightness * 0.7

        val brightPixels = roiPixels.filter { it.toInt() and 0xFF > minBrightnessThreshold }
        val avgBrightness = if (brightPixels.isNotEmpty()) {
            brightPixels.sumOf { it.toInt() and 0xFF } / brightPixels.size.toDouble()
        } else {
            0.0
        }

        roi.release()
        enhancedMat.release()
        grayMat.release()
        mat.release()

        BrightnessResult(avgBrightness, roiX, roiY, roiSize)

    } catch (e: Exception) {
        Log.e("MorseDetect", "Brightness analysis failed: ${e.message}")
        return BrightnessResult(0.0, 0, 0, 0)
    }
}
//hi work
private suspend fun Context.getCameraProvider(): ProcessCameraProvider =
    suspendCoroutine { continuation ->
        ProcessCameraProvider.getInstance(this).also { cameraProvider ->
            cameraProvider.addListener({
                continuation.resume(cameraProvider.get())
            }, ContextCompat.getMainExecutor(this))
        }
    }