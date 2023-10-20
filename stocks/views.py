from rest_framework import status, views
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from user_management.permissions import IsUser

from .models import Stock
from .serializers import StockSerializer


class StockView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAdminUser()]

    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response({"stocks": serializer.data})

    def post(self, request):
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Stock was created successfully.",
                    "stock": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockDetailView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method in ("PUT", "DELETE"):
            return [IsAdminUser()]
        return [IsAdminUser()]

    def get(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk)
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        except Stock.DoesNotExist:
            return Response(
                {"message": f"Stock/{pk} does't exist."}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk)
        except Stock.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = StockSerializer(stock, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk)
            # noticed all users who subscribed about delete stock
            stock.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Stock.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
