from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max, Count, Q

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    body = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.sender} to {self.recipient}: {self.body[:20]}..."
    
    @classmethod
    def send_message(cls, sender, recipient, body):
    # Create just ONE message record
        message = cls(
            user=recipient,  # This is the recipient's copy
            sender=sender,
            recipient=recipient,
            body=body,
            is_read=False
            )
        message.save()
        return message
    
    @classmethod
    def get_messages(cls, user):
    # Get all unique conversations where user is recipient
        received_conversations = cls.objects.filter(recipient=user).values(
        'sender'
        ).annotate(
        last=Max('date'),
        unread_count=Count('id', filter=Q(is_read=False))
    ).order_by('-last')
    
    # Get all unique conversations where user is sender
        sent_conversations = cls.objects.filter(sender=user).values(
        'recipient'
    ).annotate(
        last=Max('date')
    ).order_by('-last')
    
        conversations = []
        participants = set()
    
    # Process received messages (these can have unread counts)
        for conv in received_conversations:
            sender = User.objects.get(pk=conv['sender'])
            participants.add(sender)
            conversations.append({
            'user': sender,
            'last': conv['last'],
            'unread': conv['unread_count']
        })
    
    # Process sent messages (no unread counts for messages you sent)
        for conv in sent_conversations:
            recipient = User.objects.get(pk=conv['recipient'])
            if recipient not in participants:
                conversations.append({
                'user': recipient,
                'last': conv['last'],
                'unread': 0
            })
    
    # Sort all conversations by most recent
        conversations.sort(key=lambda x: x['last'], reverse=True)
        return conversations
    
    # @classmethod
    # def get_messages(cls, user):
  
    #     sent_conversations = cls.objects.filter(sender=user).values('recipient').annotate(last=Max('date'))
    #     received_conversations = cls.objects.filter(recipient=user).values('sender').annotate(last=Max('date'))
    
    #     conversations = []
    #     participants = set()
    
 
    #     for conv in received_conversations:
    #         sender = User.objects.get(pk=conv['sender'])
    #         participants.add(sender)
    #         conversations.append({
    #             'user': sender,
    #             'last': conv['last'],
    #             'unread': cls.objects.filter(
    #                 sender=sender,
    #                 recipient=user,
    #                 is_read=False
    #             ).count()
    #         })
    
   
    #     for conv in sent_conversations:
    #         recipient = User.objects.get(pk=conv['recipient'])
    #         if recipient not in participants:
    #             conversations.append({
    #                 'user': recipient,
    #                 'last': conv['last'],
    #                 'unread': 0  
    #             })
    
   
    #     conversations.sort(key=lambda x: x['last'], reverse=True)
    #     return conversations
