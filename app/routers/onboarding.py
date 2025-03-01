from fastapi import APIRouter, Depends, HTTPException
from google.cloud import firestore
from typing import List
from app.models.model_types import OnboardingTask, OnboardingTaskUpdate
from app.controllers.auth import UserAuth

router = APIRouter()

# Firestore client initialization
db = firestore.Client()

@router.get("/api/onboarding/tutorial")
async def get_onboarding_tutorial(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve a tutorial for new users to help them understand how to use the app.
    """
    try:
        # Fetch tutorial from Firestore (could be a video link, text, etc.)
        tutorial_ref = db.collection("onboarding").document("tutorial")
        tutorial_doc = tutorial_ref.get()

        if not tutorial_doc.exists:
            raise HTTPException(status_code=404, detail="Tutorial not found.")

        tutorial_data = tutorial_doc.to_dict()
        return {"tutorial": tutorial_data["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tutorial: {str(e)}")

# /onboarding/tutorial (document)
#     - content: "Welcome to GDGKisaanDvaar! Here's how you can list your products..."
#     - video_url: "https://example.com/tutorial_video"

@router.get("/api/onboarding/tips")
async def get_onboarding_tips(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve tips for users to help them navigate and get the most out of the app.
    """
    try:
        # Fetch tips from Firestore
        tips_ref = db.collection("onboarding").document("tips")
        tips_doc = tips_ref.get()

        if not tips_doc.exists:
            raise HTTPException(status_code=404, detail="Tips not found.")

        tips_data = tips_doc.to_dict()
        return {"tips": tips_data["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tips: {str(e)}")


# /onboarding/tips (document)
#     - content: "Tip 1: Keep your inventory up to date to attract more buyers!"
#     - content: "Tip 2: Use the chat feature to communicate directly with customers."



@router.get("/api/onboarding/checklist")
async def get_onboarding_checklist(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve a checklist of onboarding tasks for new users.
    """
    try:
        # Fetch checklist from Firestore
        checklist_ref = db.collection("onboarding").document("checklist")
        checklist_doc = checklist_ref.get()

        if not checklist_doc.exists:
            raise HTTPException(status_code=404, detail="Checklist not found.")

        checklist_data = checklist_doc.to_dict()
        tasks = checklist_data.get("tasks", [])

        # Return the checklist with task names and completion statuses
        return {"checklist": [OnboardingTask(**task) for task in tasks]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch checklist: {str(e)}")

# /onboarding/checklist (document)
#     - tasks: 
#         - {task_id: "1", task_name: "Add your first product", completed: false}
#         - {task_id: "2", task_name: "Complete your profile", completed: false}

# Example of Real-Time Update with Firestore:
# In addition to retrieving data, you could allow users to receive real-time updates for onboarding tasks by using Firestore listeners. For instance:


# # Real-time listener to track onboarding task updates (client-side example in JavaScript):
# const db = firebase.firestore();
# const checklistRef = db.collection('onboarding').doc('checklist');

# checklistRef.onSnapshot((doc) => {
#     console.log("Real-time checklist update:", doc.data());
# });
# This way, when a user completes a task, the checklist will be updated in real time.


@router.put("/api/onboarding/update-progress")
async def update_task_progress(task_update: OnboardingTaskUpdate, user=Depends(UserAuth.get_current_user)):
    """
    Update progress of onboarding tasks (mark task as completed).
    """
    try:
        # Update the task progress in Firestore
        onboarding_ref = db.collection("onboarding").document(user.uid).collection("tasks").document(task_update.task_id)
        
        # Check if task exists
        task_doc = onboarding_ref.get()
        if not task_doc.exists:
            raise HTTPException(status_code=404, detail="Task not found.")
        
        # Update the task completion status
        onboarding_ref.update({"completed": task_update.completed})

        return {"message": "Task progress updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task progress: {str(e)}")

# // Real-time listener to track onboarding task progress
# const db = firebase.firestore();
# const taskRef = db.collection('onboarding').doc(userId).collection('tasks');

# taskRef.onSnapshot((snapshot) => {
#   snapshot.docChanges().forEach((change) => {
#     if (change.type === "modified") {
#       console.log("Task progress updated: ", change.doc.data());
#     }
#   });
# });
