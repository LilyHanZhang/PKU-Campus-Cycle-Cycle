## Completion Timeline

Seller registers car information -> **After receiving the car information, the admin can reject the transaction and provide a reason; the admin can also propose several (>=1) time slots when the admin is available -> The seller receives a notification and can choose one of the time slots -> The admin confirms the time slot chosen by the seller -> The seller receives a notification, and both parties proceed with the offline transaction** -> The admin confirms the transaction, and the bicycle is added to the inventory; **the seller receives a reminder and can leave a review**

Buyer selects a bicycle from the inventory -> The bicycle is temporarily locked -> After receiving the bicycle information, the admin can reject the transaction and provide a reason; the admin proposes several (>=1) available time slots -> **The buyer receives a notification and can choose one of the time slots -> The admin confirms the time slot chosen by the buyer -> The buyer receives a notification, and both parties proceed with the offline transaction**; the buyer receives a reminder and can leave a review

During the period from when the seller/buyer registers until the offline transaction takes place, the seller/buyer can cancel the transaction at any time, and the admin can also reject the transaction at any time, providing a reason. From the time the admin proposes time slots to the actual offline transaction, the time slot can also be changed. The user will be notified again, and the user can proceed with the transaction based on the new time slot.

## To do
- now after the admin proposes time slots, the user can see it. But after they choose a time slot, there's a notification that for them to "等待管理员确认“. But the admin could not confirm this, and the procedure cannot continue. Fix this problem both for seller and buyer.
- For the seller  process, after the admin choose the time slots, the bicyle turns into "已锁定" status. However, the admin should be able to handle the bicyle (such as store it in the invertory when off-line transaction was done). 
- Both the user and admin should be able to cancel the transaction
- The notification feature now still does not work.


## Additional Features

- Add a private messaging feature. Admins can send private messages to sellers/buyers. Sellers and buyers can also send private messages to any admin.
- Add a module on the homepage. If the user and admin have already selected a time slot, the module will display how much time remains until the transaction; if no time slot has been selected yet, it will simply show that there are pending transactions.

## Page Beautification

- When selecting a time slot, add a calendar and time picker to allow users to choose the time slot.
- The page background can be enhanced with relevant images.

