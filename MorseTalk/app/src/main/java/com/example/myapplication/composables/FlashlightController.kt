package com.example.myapplication.composables

import android.content.Context
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.concurrent.ExecutionException

class FlashlightController(private val context: Context) {

    private var cameraControl: androidx.camera.core.CameraControl? = null
    private var cameraProvider: ProcessCameraProvider? = null
    private val textToMorse = TextToMorse() // Instance of TextToMorse (not used now)

    private val morseMap = mapOf(
        "A" to ".-", "B" to "-...", "C" to "-.-.", "D" to "-..", "E" to ".",
        "F" to "..-.", "G" to "--.", "H" to "....", "I" to "..", "J" to ".---",
        "K" to "-.-", "L" to ".-..", "M" to "--", "N" to "-.", "O" to "---",
        "P" to ".--.", "Q" to "--.-", "R" to ".-.", "S" to "...", "T" to "-",
        "U" to "..-", "V" to "...-", "W" to ".--", "X" to "-..-", "Y" to "-.--",
        "Z" to "--..", " " to "..--" // Space maps to ..--
    )

    init {
        Log.d("FlashTransmit", "FlashlightController initialized")
        initializeCameraControl()
    }

    private fun initializeCameraControl() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        cameraProviderFuture.addListener({
            try {
                cameraProvider = cameraProviderFuture.get()
                val camera = cameraProvider?.bindToLifecycle(
                    context as androidx.lifecycle.LifecycleOwner,
                    CameraSelector.DEFAULT_BACK_CAMERA
                )
                cameraControl = camera?.cameraControl
                Log.d("FlashTransmit", "Camera bound successfully: ${cameraControl != null}")
            } catch (e: ExecutionException) {
                Log.e("FlashTransmit", "Camera binding failed: ${e.message}")
            }
        }, ContextCompat.getMainExecutor(context))
    }

    fun turnOnFlashlight() {
        cameraControl?.enableTorch(true) ?: Log.w("FlashTransmit", "Failed to turn on flashlight: cameraControl is null")
    }

    fun turnOffFlashlight() {
        cameraControl?.enableTorch(false) ?: Log.w("FlashTransmit", "Failed to turn off flashlight: cameraControl is null")
    }

    fun transmitMorseCode(input: String) {
        CoroutineScope(Dispatchers.IO).launch {
            Log.d("FlashTransmit", "Starting transmission with input: '$input'")
            delay(1000) // Initial delay to ensure receiver is ready

            // Convert input to Morse code using morseMap, preserving spaces
            val morseSequence = input.uppercase().map { char ->
                morseMap[char.toString()] ?: "" // Map each character, including space
            }.filter { it.isNotEmpty() }.joinToString(" ")
            Log.d("FlashTransmit", "Full Morse sequence: '$morseSequence'")

            var flashCount = 0
            for (char in morseSequence) {
                Log.d("FlashTransmit", "Processing character: '$char'")
                when (char) {
                    '.' -> {
                        blink(200) // Dot duration
                        flashCount++
                    }
                    '-' -> {
                        blink(600) // Dash duration
                        flashCount++
                    }
                    ' ' -> {
                        delay(1000) // Letter gap between Morse symbols
                        Log.d("FlashTransmit", "Letter gap (1000ms)")
                    }
                }
            }
            Log.d("FlashTransmit", "Transmission complete. Total flashes: $flashCount")
        }
    }

    private suspend fun blink(duration: Long) {
        turnOnFlashlight()
        Log.d("FlashTransmit", "Flash ON for ${duration}ms")
        delay(duration)
        turnOffFlashlight()
        Log.d("FlashTransmit", "Flash OFF for 400ms")
        delay(400) // Gap between dots and dashes within a letter
    }
}