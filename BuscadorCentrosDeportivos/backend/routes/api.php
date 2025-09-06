<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\SportsCenterController;

Route::middleware('api')->group(function () {
    Route::get('/sports-centers', [SportsCenterController::class, 'index']);
    Route::get('/sports-centers/{sportsCenter}', [SportsCenterController::class, 'show']);
}); 