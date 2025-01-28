# Installed packages
from datetime import datetime

# Local packages
from .database import (
    products_collection,
    users_collection,
    reports_collection,
    locations_collection,
)
from .service import allocate_product_warehouse
from .config import RACK_SIZE, SHELF_SIZE, FLOOR_LEVELS


class Warehouse:
    def __init__(self):
        self.products_collection = products_collection
        self.users_collection = users_collection
        self.reports_collection = reports_collection
        self.locations_collection = locations_collection
        self.current_date = datetime.now().date()

        # self.RACK_SIZE = 5
        # self.SHELF_SIZE = 10
        # self.FLOOR_LEVELS = 3
        #
        # self.N =

    async def pick_workers(self, product_id, schedule, place, time, workers_list):
        pass

    # async def calculate_allocation(self, product_id, weight, booking_date):
    #     """
    #     Method for calculating optimally an allocation for approved product in a stock.
    #     The idea is to first know the total number of RACK_SIZE, FLOOR_LEVELS, SHELF_SIZE.
    #
    #     """
    #
    # allocated_row = 0
    # allocated_floor_level = 0
    # allocated_shelf = 0
    # # Create a data structure to track the availability of each row, shelf, and floor level
    # availability = [[[True] * (SHELF_SIZE + 1) for _ in range(FLOOR_LEVELS + 1)] for _ in range(RACK_SIZE + 1)]
    #
    # # Get documents that are already allocated in the stock with projected fields
    # # warehouse_row, floor_level, shelf_num, weight, booking_date sorted by
    # distinct_values = await locations_collection.find(
    #     {'warehouse_row': {'$ne': 0}, 'floor_level': {'$ne': 0}, 'shelf_num': {'$ne': 0}},
    #     {'warehouse_row': 1, 'floor_level': 1, 'shelf_num': 1, 'weight': 1, 'booking_date': 1}
    # ).sort([('warehouse_row', 1), ('floor_level', 1), ('shelf_num', 1)]).to_list(None)
    #
    # for doc in distinct_values:
    #     row = doc['warehouse_row']
    #     floor = doc['floor_level']
    #     shelf = doc['shelf_num']
    #
    #     availability[row][floor][shelf] = False
    # print(availability)
    # if all(all(row) for floor_level in availability for row in floor_level):
    #     print("Here")
    #     await allocate_product_warehouse(product_id, 1, 1, 1)
    #     return
    #
    # proximity_weight_scores = {}
    # proximity_date_scores = {}
    # for doc in distinct_values:
    #     row = doc['warehouse_row']
    #     floor = doc['floor_level']
    #     shelf = doc['shelf_num']
    #
    #     booking_date1 = booking_date
    #     booking_date2 = doc['booking_date']
    #
    #     proximity_weight_scores[(row, floor, shelf)] = abs(weight - doc['weight'])
    #     proximity_date_scores[(row, floor, shelf)] = abs(booking_date1 - booking_date2)
    #
    # # Sort first by proximity_weight_scores, then by proximity_date_scores
    # sorted_rows = sorted(proximity_weight_scores.keys(),
    #                      key=lambda x: (proximity_weight_scores[x], proximity_date_scores[x]))
    #
    # # Create a priority queue to store the best fit positions based on proximity scores
    #
    # best_fit = None
    # best_fit_weight_diff = float('inf')
    # best_fit_booking_date_diff = float('inf')
    # weight_diff = None
    # booking_date_diff = None
    #
    # prev_diff_weight = None
    # prev_diff_date = None
    #
    # # Iterate through the rows, floor levels, and shelves to calculate proximity scores and store in the queue
    # for row in range(1, RACK_SIZE + 1):
    #     for floor in range(1, FLOOR_LEVELS + 1):
    #         check_floor = False
    #         for shelf in range(1, SHELF_SIZE + 1):
    #             if not availability[row][floor][shelf]:
    #                 prev_diff_weight = weight_diff
    #
    #                 prev_diff_date = booking_date_diff
    #
    #                 weight_diff = proximity_weight_scores.get((row, floor, shelf), float("inf"))
    #                 booking_date_diff = proximity_date_scores.get((row, floor, shelf), float("inf"))
    #                 print(f"{row}, {floor}, {shelf}: Weight {weight_diff}, Booking_date {booking_date_diff}")
    #                 if weight_diff < best_fit_weight_diff or (weight_diff == best_fit_weight_diff and booking_date_diff <= best_fit_booking_date_diff):
    #                     best_fit_weight_diff = weight_diff
    #                     best_fit_booking_date_diff = booking_date_diff
    #             else:
    #                 if not (prev_diff_weight or prev_diff_date) or (prev_diff_weight != best_fit_weight_diff or booking_date_diff != best_fit_booking_date_diff):
    #                     best_fit = (row, floor, shelf)
    #                     check_floor = True
    #                     break
    #         if check_floor:
    #             break
    #
    #     if best_fit:
    #         allocated_row, allocated_floor_level, allocated_shelf = best_fit
    #         break
    # if allocated_row != 0 and allocated_shelf != 0 and allocated_floor_level != 0:
    #     # Allocate the product to the identified row, floor level, and shelf combination
    #     await allocate_product_warehouse(product_id, allocated_row, allocated_floor_level, allocated_shelf)
    #     return

    async def calculate_allocation(self, product_id, weight, booking_date):
        # Create a data structure to track the availability of each row, shelf, and floor level
        availability = [
            [[True] * (SHELF_SIZE + 1) for _ in range(FLOOR_LEVELS + 1)]
            for _ in range(RACK_SIZE + 1)
        ]

        occupied_locations = (
            await self.locations_collection.find(
                {"product_id": {"$ne": None}},
                {"warehouse_row": 1, "floor_level": 1, "shelf_num": 1, "product_id": 1},
            )
            .sort([("warehouse_row", 1), ("floor_level", 1), ("shelf_num", 1)])
            .to_list(None)
        )

        allocated_products = await self.products_collection.find(
            {"location_id": {"$exists": True}},
            {"weight": 1, "booking_date": 1, "location_id": 1},
        ).to_list(None)

        matched_data = []

        for location in occupied_locations:
            for product in allocated_products:
                if location["_id"] == product["location_id"]:
                    matched_data.append({"product": product, "location": location})

        for doc in matched_data:
            row = doc["location"]["warehouse_row"]
            floor = doc["location"]["floor_level"]
            shelf = doc["location"]["shelf_num"]

            availability[row][floor][shelf] = False

        for row in range(1, RACK_SIZE + 1):
            for floor in range(1, FLOOR_LEVELS + 1):
                for shelf in range(1, SHELF_SIZE + 1):
                    if availability[row][floor][shelf]:
                        await allocate_product_warehouse(product_id, row, floor, shelf)
                        return row, floor, shelf
        # await handle_unallocated_product(product_id)
