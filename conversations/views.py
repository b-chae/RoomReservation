from django.utils import timezone
from django.http import Http404
from django.shortcuts import redirect, reverse, render
from django.views.generic import View
from users import models as user_models
from . import models, forms


def go_conversation(request, a_pk, b_pk):
    user_one = user_models.User.objects.get(pk=a_pk)
    user_two = user_models.User.objects.get(pk=b_pk)
    if user_one is not None and user_two is not None:
        try:
            conversation = models.Conversation.objects.filter(
                participants=user_one).filter(participants=user_two)[0]
        except Exception:
            conversation = models.Conversation.objects.create()
            conversation.participants.add(user_one, user_two)

        return redirect(
            reverse("conversations:detail",
                    kwargs={"pk": conversation.pk}))


class ConversationDetailView(View):

    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()

        if not self.request.user.is_authenticated:
            return render(redirect("users:login"))

        if self.request.user not in conversation.participants.all():
            raise Http404()

        form = forms.AddCommentForm
        return render(self.request, "conversations/conversation_detail.html",
                      {"conversation": conversation,
                       "form": form})

    def post(self, *args, **kwargs):
        message = self.request.POST.get('message')
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if message is not None:
            models.Message.objects.create(
                message=message,
                user=self.request.user,
                conversation=conversation,
            )
        conversation.save()
        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
