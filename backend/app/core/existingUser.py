from app.models.user_info import User_Info
from app.models.threads import Thread
from bson import ObjectId


async def step_check(thread_id, flow, total_step):
    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    user = await User_Info.find_one(User_Info.thread_id == thread_id)
    user_message = ""
    if user:
        for i in range(1, total_step + 1):
            if str(i) == "1" and user.name:
                thread.step_id = flow["steps"]["1"]["next_step"]
                await thread.save()
                user_message = user.name
            elif str(i) == "2" and user.name and user.phone_number:
                thread.step_id = flow["steps"]["2"]["next_step"]
                await thread.save()
                user_message = user.phone_number
            elif str(i) == "3" and user.phone_number and "3" in flow["steps"]:
                thread.step_id = flow["steps"]["3"]["next_step"]
                await thread.save()
                user_message = user.phone_number
            elif (
                str(i) == "5" and user.pincode and user.name
            ):  # and user.preffered_center
                if thread.flow_id != "book_appointment":
                    user_message = str(user.pincode)
            elif str(i) == "6" and user.checkup_date:
                thread.step_id = flow["steps"]["6"]["next_step"]
                await thread.save()
                user_message = user.checkup_date
            elif str(i) == "7" and user.checkup_time_slot:
                thread.step_id = flow["steps"]["7"]["next_step"]
                await thread.save()
                user_message = user.checkup_time_slot
            else:
                continue
        return user_message
    return None
