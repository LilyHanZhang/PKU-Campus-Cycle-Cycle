# Buyer and Seller Flow Fixes

## Summary
Fixed both buyer and seller transaction flows to properly handle time slot selection and appointment confirmation.

## Issues Fixed

### 1. Seller Flow (PENDING_APPROVAL → IN_STOCK → LOCKED → RESERVED → IN_STOCK)
**Issue**: Administrators couldn't propose time slots for PENDING_APPROVAL bicycles without existing appointments.

**Solution**:
- Modified `propose_time_slots()` in `bicycles.py` to handle PENDING_APPROVAL status
- Automatically creates pick-up type time slots for seller flow
- Added `confirm_bicycle_time_slot()` endpoint in `time_slots.py` for confirming seller-selected time slots
- Created appointment record when seller selects time slot

**Flow**:
1. Seller registers bicycle → `PENDING_APPROVAL`
2. Admin proposes time slots → `IN_STOCK` → `LOCKED`
3. Seller selects time slot → `LOCKED`
4. Admin confirms → `RESERVED`
5. Admin stores inventory after offline transaction → `IN_STOCK`

### 2. Buyer Flow (PENDING_APPROVAL → IN_STOCK → LOCKED → SOLD)
**Issue**: 
- Administrators couldn't propose time slots for IN_STOCK bicycles
- No appointment was created for buyer flow
- Time slot selection didn't update appointment records

**Solution**:
- Modified `propose_time_slots()` to handle IN_STOCK status
- Creates pick-up type appointment for buyer flow
- Updated `select_bicycle_time_slot()` to update appointment's `time_slot_id`
- Fixed appointment type: pick-up for buyer flow (→ SOLD after confirmation)

**Flow**:
1. Buyer registers bicycle → `PENDING_APPROVAL`
2. Admin approves → `IN_STOCK`
3. Admin proposes time slots → `LOCKED` (creates appointment)
4. Buyer selects time slot → `LOCKED` (updates appointment)
5. Admin confirms → `SOLD`

## Files Modified

### Backend
1. `backend/app/routers/bicycles.py`
   - Updated `propose_time_slots()` to support both seller and buyer flows
   - Creates appointments for IN_STOCK status (buyer flow)

2. `backend/app/routers/time_slots.py`
   - Added `confirm_bicycle_time_slot()` endpoint for seller flow confirmation
   - Updated `select_bicycle_time_slot()` to update appointment records
   - Fixed status transitions in `confirm_time_slot()`

### Tests
1. `tests/unit/test_buyer_flow.py` - Pytest unit tests for buyer flow (5 tests)
2. `test_buyer_flow.py` - Integration test for complete buyer flow
3. `test_complete_seller_flow.py` - Integration test for complete seller flow

## API Endpoints

### Seller Flow
- `POST /bicycles/{bike_id}/propose-slots` - Admin proposes time slots
- `GET /time_slots/bicycle/{bike_id}` - Seller views available slots
- `PUT /time_slots/select-bicycle/{bike_id}` - Seller selects time slot
- `PUT /time_slots/confirm-bicycle/{bike_id}` - Admin confirms seller-selected slot
- `PUT /bicycles/{bike_id}/store-inventory` - Admin stores inventory after offline transaction

### Buyer Flow
- `PUT /bicycles/{bike_id}/approve` - Admin approves bicycle
- `POST /bicycles/{bike_id}/propose-slots` - Admin proposes time slots
- `GET /time_slots/bicycle/{bike_id}` - Buyer views available slots
- `PUT /time_slots/select-bicycle/{bike_id}` - Buyer selects time slot
- `PUT /time_slots/confirm/{apt_id}` - Admin confirms appointment (→ SOLD)

## Testing

### Run Buyer Flow Tests
```bash
# Integration test
python test_buyer_flow.py

# Unit tests
python -m pytest tests/unit/test_buyer_flow.py -v
```

### Run Seller Flow Tests
```bash
# Integration test
python test_complete_seller_flow.py

# Unit tests
python -m pytest tests/unit/test_seller_propose_slots_final.py -v
```

## Status Transitions

### Seller Flow
```
PENDING_APPROVAL → (admin proposes) → IN_STOCK → LOCKED → (seller selects) → LOCKED → (admin confirms) → RESERVED → (store inventory) → IN_STOCK
```

### Buyer Flow
```
PENDING_APPROVAL → (admin approves) → IN_STOCK → (admin proposes) → LOCKED → (buyer selects) → LOCKED → (admin confirms) → SOLD
```

## Key Differences

| Aspect | Seller Flow | Buyer Flow |
|--------|-------------|------------|
| Initial Status | PENDING_APPROVAL | PENDING_APPROVAL |
| After Admin Proposes | LOCKED | LOCKED |
| Appointment Type | pick-up (seller delivers) | pick-up (buyer picks up) |
| After Confirmation | RESERVED | SOLD |
| Final Step | Store inventory (IN_STOCK) | Transaction complete (SOLD) |

## Deployment
All changes have been deployed to Render. Wait 2-3 minutes after push for deployment to complete.
