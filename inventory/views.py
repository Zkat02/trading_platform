from rest_framework import views
from rest_framework.response import Response

from inventory.serializers import InventorySerializer
from inventory.services import InventoryService
from user_management.permissions import IsUser

inventory_service = InventoryService()


class InventoryView(views.APIView):
    permission_classes = [IsUser]

    def get(self, request):
        inventory = inventory_service.get_user_inventory(user_id=request.user.id)
        serializer = InventorySerializer(inventory, many=True)
        return Response({"inventory": serializer.data})
