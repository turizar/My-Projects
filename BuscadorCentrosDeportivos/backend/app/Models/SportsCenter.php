<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SportsCenter extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'description',
        'image_url',
        'address',
        'phone',
        'schedule',
        'price_type',
        'price',
        'latitude',
        'longitude',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'latitude' => 'decimal:8',
        'longitude' => 'decimal:8',
    ];

    public function sports()
    {
        return $this->belongsToMany(Sport::class);
    }

    public function getFormattedPriceAttribute()
    {
        if ($this->price_type === 'free') {
            return 'Gratis';
        }
        return '$' . number_format($this->price, 0, ',', '.');
    }
} 