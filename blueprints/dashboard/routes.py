from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from extensions import supabase, supabase_admin
import logging, traceback
from functools import wraps
import requests
import json
import uuid
import os


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id", False):
            return redirect(url_for("auth.login_get"))
        try:
            user_id = session["user_id"]
            user = supabase_admin.auth.admin.get_user_by_id(user_id).user
            if not user:
                session.clear()
                return redirect(url_for("auth.login_get"))
        except Exception as e:
            print(f"An unexpected error occurred during session validation: {e}")
            session.clear()
            return redirect(url_for("auth.login_get"))
        return f(user.user_metadata, *args, **kwargs)

    return decorated_function


@dashboard_bp.route("/", methods=["GET", "POST"])
@login_required
def home(user):
    email = session["user"]
    if request.method == "POST":
        prompt = request.form.get("prompt")
        unique_id = str(uuid.uuid4())
        selected_images = request.form.getlist("images")
        url = "https://secret-api-gt36.onrender.com/webhook/generate-image"
        payload = {
            "email": session["user"],
            "id": unique_id,
            "data": {
                "model": "seedream-4-0-250828",
                "prompt": prompt,
                "image": selected_images,
                "size": "2K",
            },
        }
        headers = {"Content-Type": "application/json"}
        try:
            requests.post(url, headers=headers, data=json.dumps(payload))
            flash("Job submitted successfully.", "success")
        except Exception as e:
            logging.error("Image generation failed: %s\n%s", e, traceback.format_exc())
            print(f"Error during image generation: {e}", flush=True)
            flash("Failed to generate image.", "danger")
        return redirect(url_for("dashboard.home"))

    all_files = supabase_admin.storage.from_(email).list("my_images")
    images = [
        {
            "name": f["name"],
            "url": f"https://ntvibateqvasbeygcsvr.supabase.co/storage/v1/object/public/{email}/my_images/{f['name']}",
        }
        for f in all_files
        if not f["name"].endswith(".emptyFolderPlaceholder")
    ]

    return render_template(
        "dashboard/dashboard.html",
        user=user,
        restricted=not user.get("email_verified"),
        images=images
    )


@dashboard_bp.get("/jobs")
@login_required
def jobs(user):
    page = session.get("page", 0)

    response = (
        supabase.table("jobs")
        .select("id, status, created_at, email, prompt")
        .eq("email", session["user"])
        .order("created_at", desc=True)
        .execute()
    )

    jobs = response.data if response.data else []

    pending_jobs = len([job for job in jobs if not job["status"]])
    done_jobs = len(jobs) - pending_jobs

    return render_template(
        "dashboard/jobs.html",
        jobs=jobs,
        pending_jobs=pending_jobs,
        done_jobs=done_jobs,
        page=page,
        user=user,
    )


@dashboard_bp.get("/profile")
@login_required
def profile(user):
    return render_template("dashboard/profile.html", user=user)

@dashboard_bp.route("/basket", methods=["GET", "POST"])
@login_required
def basket(user):
    email = session["user"]
    if request.method == "POST":
        uploaded_files = request.files.getlist("new_images")

        for file in uploaded_files:
            if file.filename:
                filename = f"{uuid.uuid4()}.jpeg"
                path = f"my_images/{filename}"
                file.stream.seek(0)
                supabase_admin.storage.from_(email).upload(
                    path, file.stream.read(), {"content-type": file.content_type}
                )

        return redirect(url_for("dashboard.basket"))
    all_files = supabase_admin.storage.from_(email).list("my_images")
    images = [
        {
            "name": f["name"],
            "url": f"https://ntvibateqvasbeygcsvr.supabase.co/storage/v1/object/public/{email}/my_images/{f['name']}",
        }
        for f in all_files
        if not f["name"].endswith(".emptyFolderPlaceholder")
    ]

    return render_template("dashboard/basket.html", user=user, images=images)

@dashboard_bp.route("/basket/delete", methods=["POST"])
@login_required
def delete_image(user):
    email = session["user"]
    to_delete = request.form.getlist("delete_images")

    if to_delete:
        paths = [f"my_images/{name}" for name in to_delete]
        supabase_admin.storage.from_(email).remove(paths)

    return redirect(url_for("dashboard.basket"))



@dashboard_bp.post("/reset_password")
def reset():
    password = request.form.get("password")
    try:
        supabase.auth.update_user({"password": password})
        flash("Password reset succesfully.", "reset_success")
    except Exception as e:
        print(str(e))
        flash(str(e), "reset_danger")
    return redirect(url_for("dashboard.dashboard_user"))
