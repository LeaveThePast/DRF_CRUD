from rest_framework import serializers

from logistic.models import Product, StockProduct, Stock


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['address', 'positions']

    def create(self, validated_data):
        positions = validated_data.pop('positions')
        stock = super().create(validated_data)

        for position in positions:
            product = position.get('product')
            quantity = position.get('quantity')
            price = position.get('price')
            if product and quantity and price:
                StockProduct.objects.create(stock=stock, product=product, quantity=quantity, price=price)
            else:
                raise serializers.ValidationError("Invalid product position data")

        return stock

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        stock = super().update(instance, validated_data)

        for position in positions:
            product = position.get('product')
            quantity = position.get('quantity')
            price = position.get('price')

            if not product or not quantity or not price:
                raise serializers.ValidationError("Invalid product position data")

            stock_product, created = StockProduct.objects.get_or_create(
                stock=stock, product=product,
                defaults={'quantity': quantity, 'price': price}
            )

            if not created:
                stock_product.quantity = quantity
                stock_product.price = price
                stock_product.save()
        return stock


class ProductSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class StockSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'address']


class PaginationSerializer(serializers.Serializer):
    next_page = serializers.IntegerField()
    prev_page = serializers.IntegerField()
    count = serializers.IntegerField()
    page_size = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())