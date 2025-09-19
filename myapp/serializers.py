from rest_framework import serializers
from .models import financial_info, Results



class ResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = ["revenue", "cos"]

class Financial_InfoSerializers (serializers.ModelSerializer):
    results=ResultsSerializer()
    class Meta:
        model = financial_info
        fields =  fields = ["period_end_date", "results"]

class ExtractRequestSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    period_end_date = serializers.DateField(required=False)

