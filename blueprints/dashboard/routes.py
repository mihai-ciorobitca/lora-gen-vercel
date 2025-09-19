from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from extensions import supabase, supabase_admin
import logging, traceback
from functools import wraps
import requests
import json
import uuid


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


@dashboard_bp.get("/")
@login_required
def dashboard_get(user):
    email_verified = user.get("email_verified")

    try:
        response = (
            supabase.table("jobs")
            .select("id, created_at, prompt, email")
            .eq("email", session["user"])
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )
        last_jobs = response.data if response.data else []
    except Exception as e:
        last_jobs = []
        flash("Could not load jobs.", "danger")

    return render_template(
        "dashboard/dashboard.html",
        user=user,
        last_jobs=last_jobs,
        restricted=not email_verified,
    )


@dashboard_bp.post("/")
@login_required
def dashboard_post(user):
    prompt = request.form.get("prompt")
    unique_id = str(uuid.uuid4())
    url = "https://secret-api-gt36.onrender.com/webhook/generate-image"
    payload = {
        "email": session["user"],
        "id": unique_id,
        "data": {
            "model": "seedream-4-0-250828",
            "prompt": prompt,
            "image": [
                # TODO: user upload images
                "https://drive.google.com/uc?export=view&id=1SIzeGV7N8VZDDeVOXIjozAjUUcLXIc8W",
                "https://drive.google.com/uc?export=view&id=1bEGLvhK_KGF1qzj991VIbVeFFknjyhK7",
                "https://drive.google.com/uc?export=view&id=1YHJh-xj6dUCXhGYjeRlV7Js2YnSXcK0m",
            ],
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
    return redirect(url_for("dashboard.dashboard_get"))


@dashboard_bp.get("/jobs")
@login_required
def dashboard_jobs(user):
    page = session.get("page", 0)
    page_size = 10

    response = (
        supabase.table("jobs")
        .select("id, status, created_at, email, prompt")
        .eq("email", session["user"])
        .range(page * page_size, (page + 1) * page_size)
        .order("created_at", desc=True)
        .execute()
    )

    jobs = response.data if response.data else []

    pending_jobs = len([job for job in jobs if not job["status"]])
    done_jobs = len(jobs) - pending_jobs

    if len(jobs) > page_size:
        jobs = jobs[:page_size]
        has_next_page = True
    else:
        has_next_page = False

    return render_template(
        "dashboard/jobs.html",
        jobs=jobs,
        pending_jobs=pending_jobs,
        done_jobs=done_jobs,
        page=page,
        has_next_page=has_next_page,
        user=user,
    )


@dashboard_bp.get("/profile")
@login_required
def dashboard_user(user):
    return render_template("dashboard/profile.html", user=user)


@dashboard_bp.post("/reset_password")
def dashboard_reset():
    password = request.form.get("password")
    try:
        supabase.auth.update_user({"password": password})
        flash("Password reset succesfully.", "reset_success")
    except Exception as e:
        print(str(e))
        flash(str(e), "reset_danger")
    return redirect(url_for("dashboard.dashboard_user"))


@dashboard_bp.post("/jobs/next")
@login_required
def next_page():
    page = session.get("page", 0)
    session["page"] = page + 1
    return redirect(url_for("dashboard.dasboard_jobs"))


@dashboard_bp.post("/jobs/prev")
@login_required
def prev_page():
    page = session.get("page", 0)
    if page > 0:
        session["page"] = page - 1
    return redirect(url_for("dashboard.dasboard_jobs"))


@dashboard_bp.post("/jobs/first")
@login_required
def first_page():
    session["page"] = 0
    return redirect(url_for("dashboard.dasboard_jobs"))
