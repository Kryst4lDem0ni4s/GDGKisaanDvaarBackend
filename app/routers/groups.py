from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from firebase_admin import firestore, auth
from app.models.model_types import GroupInviteRequest, GroupRequest, UpdateGroupRequest
from firebase_admin import db
import speech_recognition as sr
import io
from typing import Optional, List
from app.controllers.auth import UserAuth


router = APIRouter()

@router.get("/api/groups")
async def get_groups():
    """
    Fetch all cooperative groups.
    """
    try:
        groups_ref = db.collection("groups").stream()
        groups = [doc.to_dict() for doc in groups_ref]
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/groups")
async def create_group(request: GroupRequest, user=Depends(UserAuth.get_current_user)):
    """
    Create a new cooperative group.
    """
    try:
        group_ref = db.collection("groups").document()
        group_data = request.dict()
        group_data["group_id"] = group_ref.id
        group_data["members"].append(request.created_by)  # Ensure creator is a member
        group_ref.set(group_data)
        return {"message": "Group created successfully", "group_id": group_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/groups/{groupId}")
async def get_group(groupId: str, user=Depends(UserAuth.get_current_user)):
    """
    Retrieve details of a specific group.
    """
    try:
        group_ref = db.collection("groups").document(groupId).get()
        if not group_ref.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        return group_ref.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/groups/{groupId}")
async def update_group(groupId: str, request: UpdateGroupRequest, user=Depends(UserAuth.get_current_user)):
    """
    Update details of a cooperative group.
    """
    try:
        group_ref = db.collection("groups").document(groupId)
        group = group_ref.get()
        if not group.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        group_ref.update(update_data)
        return {"message": "Group updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/groups")
async def get_groups():
    """
    Fetch all cooperative groups.
    """
    try:
        groups_ref = db.collection("groups").stream()
        groups = [doc.to_dict() for doc in groups_ref]
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/groups")
async def create_group(request: GroupRequest, user=Depends(UserAuth.get_current_user)):
    """
    Create a new cooperative group.
    """
    try:
        group_ref = db.collection("groups").document()
        group_data = request.dict()
        group_data["group_id"] = group_ref.id
        group_data["members"].append(request.created_by)  # Ensure creator is a member
        group_ref.set(group_data)
        return {"message": "Group created successfully", "group_id": group_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/groups/{groupId}")
async def get_group(groupId: str, user=Depends(UserAuth.get_current_user)):
    """
    Retrieve details of a specific group.
    """
    try:
        group_ref = db.collection("groups").document(groupId).get()
        if not group_ref.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        return group_ref.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/groups/{groupId}")
async def update_group(groupId: str, request: UpdateGroupRequest, user=Depends(UserAuth.get_current_user)):
    """
    Update details of a cooperative group.
    """
    try:
        group_ref = db.collection("groups").document(groupId)
        group = group_ref.get()
        if not group.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        group_ref.update(update_data)
        return {"message": "Group updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/groups/{groupId}")
async def delete_group(groupId: str, user=Depends(UserAuth.get_current_user)):
    """
    Delete a cooperative group.
    """
    try:
        group_ref = db.collection("groups").document(groupId)
        group = group_ref.get()
        if not group.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        group_ref.delete()
        return {"message": "Group deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/groups/{groupId}/members")
async def get_group_members(groupId: str, user=Depends(UserAuth.get_current_user)):
    """
    Retrieve members of a specific group.
    """
    try:
        group_ref = db.collection("groups").document(groupId).get()
        if not group_ref.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        group_data = group_ref.to_dict()
        return {"members": group_data.get("members", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/groups/{groupId}/members")
async def add_group_member(groupId: str, member_id: str, user=Depends(UserAuth.get_current_user)):
    """
    Add a member to a cooperative group.
    """
    try:
        group_ref = db.collection("groups").document(groupId)
        group = group_ref.get()
        if not group.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        group_data = group.to_dict()
        if member_id in group_data.get("members", []):
            raise HTTPException(status_code=400, detail="Member already in group")
        group_data["members"].append(member_id)
        group_ref.update({"members": group_data["members"]})
        return {"message": "Member added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/groups/{groupId}/members/{memberId}")
async def remove_group_member(groupId: str, memberId: str, user=Depends(UserAuth.get_current_user)):
    """
    Remove a member from a cooperative group.
    """
    try:
        group_ref = db.collection("groups").document(groupId)
        group = group_ref.get()
        if not group.exists:
            raise HTTPException(status_code=404, detail="Group not found")
        group_data = group.to_dict()
        if memberId not in group_data.get("members", []):
            raise HTTPException(status_code=404, detail="Member not found in group")
        group_data["members"].remove(memberId)
        group_ref.update({"members": group_data["members"]})
        return {"message": "Member removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/groups/{groupId}/invite")
async def invite_member(groupId: str, request: GroupInviteRequest, user=Depends(UserAuth.get_current_user)):
    """
    Invite a new member to a cooperative group via email.
    """
    try:
        invite_ref = db.collection("groups").document(groupId).collection("invites").document()
        invite_data = request.dict()
        invite_data["invite_id"] = invite_ref.id
        invite_data["status"] = "pending"
        invite_ref.set(invite_data)
        return {"message": "Invitation sent successfully", "invite_id": invite_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/groups/{groupId}/chat")
async def get_group_chat(groupId: str, user=Depends(UserAuth.get_current_user)):
    """
    Retrieve group chat messages for a specific group.
    """
    try:
        chat_ref = db.collection("groups").document(groupId).collection("chat").stream()
        messages = [doc.to_dict() for doc in chat_ref]
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

