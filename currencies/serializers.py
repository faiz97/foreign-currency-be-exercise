from rest_framework import serializers
from currencies.models import Currency, CurrencyRate

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = '__all__'

class CurrencyRateCreatorRequestSerializer(serializers.Serializer):
    date = serializers.DateField()
    domain = serializers.CharField(max_length=3)
    codomain = serializers.CharField(max_length=3)
    rate = serializers.FloatField()
    

