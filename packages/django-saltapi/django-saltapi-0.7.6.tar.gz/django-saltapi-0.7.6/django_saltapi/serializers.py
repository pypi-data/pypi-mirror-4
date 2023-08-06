# -*- coding: utf-8 -*-

from rest_framework import serializers

class LowdataSerializer(serializers.Serializer):
    client = serializers.CharField(max_length=20)
    tgt    = serializers.CharField(max_length=50)
    fun    = serializers.CharField(max_length=30)
    arg    = serializers.CharField(max_length=100,
                                   required=False,)
