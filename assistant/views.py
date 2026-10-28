import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShopSettings, ShopFAQ
from .services import ask_shop_assistant


@csrf_exempt
def chat_api(request):
    """API endpoint for the customer & owner AI FAQ assistant."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_msg = data.get("message", "").strip()
            if not user_msg:
                return JsonResponse({"error": "Message cannot be empty."}, status=400)
            
            ai_reply = ask_shop_assistant(user_msg)
            return JsonResponse({"reply": ai_reply})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST method required"}, status=405)


@login_required
def shop_settings_view(request):
    """Allows the shopkeeper to configure store profile & AI guidelines."""
    settings_obj, created = ShopSettings.objects.get_or_create(id=1)

    if request.method == "POST":
        settings_obj.shop_name = request.POST.get("shop_name", settings_obj.shop_name)
        settings_obj.tagline = request.POST.get("tagline", settings_obj.tagline)
        settings_obj.owner_name = request.POST.get("owner_name", settings_obj.owner_name)
        settings_obj.phone = request.POST.get("phone", settings_obj.phone)
        settings_obj.email = request.POST.get("email", settings_obj.email)
        settings_obj.address = request.POST.get("address", settings_obj.address)
        settings_obj.opening_time = request.POST.get("opening_time", settings_obj.opening_time)
        settings_obj.closing_time = request.POST.get("closing_time", settings_obj.closing_time)
        settings_obj.weekly_off = request.POST.get("weekly_off", settings_obj.weekly_off)
        settings_obj.upi_id = request.POST.get("upi_id", settings_obj.upi_id)
        settings_obj.return_policy = request.POST.get("return_policy", settings_obj.return_policy)
        new_key = request.POST.get("gemini_api_key", "").strip()
        if new_key:
            settings_obj.gemini_api_key = new_key
        settings_obj.custom_ai_instructions = request.POST.get("custom_ai_instructions", settings_obj.custom_ai_instructions)
        settings_obj.save()

        messages.success(request, "Shop settings and AI knowledge updated successfully!")
        return redirect("shop_settings")

    faqs = ShopFAQ.objects.all()
    return render(request, "assistant/settings.html", {"settings": settings_obj, "faqs": faqs})


@login_required
def add_faq_view(request):
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        answer = request.POST.get("answer", "").strip()
        if question and answer:
            ShopFAQ.objects.create(question=question, answer=answer)
            messages.success(request, "New FAQ added to AI knowledge base.")
        else:
            messages.error(request, "Both question and answer are required.")
    return redirect("shop_settings")


@login_required
def delete_faq_view(request, faq_id):
    faq = get_object_or_404(ShopFAQ, id=faq_id)
    faq.delete()
    messages.success(request, "FAQ removed from AI knowledge base.")
    return redirect("shop_settings")
