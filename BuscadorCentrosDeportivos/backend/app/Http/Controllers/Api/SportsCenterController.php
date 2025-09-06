<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\SportsCenter;
use Illuminate\Http\Request;

class SportsCenterController extends Controller
{
    public function index(Request $request)
    {
        $query = SportsCenter::with('sports');

        // Filter by search term
        if ($request->has('search')) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', "%{$search}%")
                  ->orWhere('description', 'like', "%{$search}%")
                  ->orWhere('address', 'like', "%{$search}%");
            });
        }

        // Filter by sport
        if ($request->has('sport')) {
            $query->whereHas('sports', function ($q) use ($request) {
                $q->where('slug', $request->sport);
            });
        }

        // Filter by price type
        if ($request->has('price_type')) {
            $query->where('price_type', $request->price_type);
        }

        // Sort by name
        $query->orderBy('name');

        return response()->json($query->paginate(12));
    }

    public function show(SportsCenter $sportsCenter)
    {
        return response()->json($sportsCenter->load('sports'));
    }
} 