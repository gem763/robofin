from rest_framework import serializers
from .models import Asset, Marketdata

# class AssetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Asset
#         fields = ('ticker', 'name', )
#         read_only_fields = fields


def get_assetSerializer(flds=None):
    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Asset
            fields = ('ticker', 'name', ) if flds is None else flds
            read_only_fields = fields

    return Serializer


def get_marketdataSerializer(flds=None):
    class Serializer(serializers.ModelSerializer):
        ticker = serializers.CharField(source='asset.ticker')

        class Meta:
            model = Marketdata
            fields = ['ticker', 'date', 'price', 'nshares', 'tradable', 'amount'] if flds is None else flds
            read_only_fields = fields

        # def to_representation(self, instance):
        #     data = super(Serializer, self).to_representation(instance)
        #     return dict(data)

    return Serializer
