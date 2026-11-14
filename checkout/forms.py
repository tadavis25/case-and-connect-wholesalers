from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, label="First name")
    last_name = forms.CharField(max_length=100, label="Last name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].required = False

    class Meta:
        model = Order
        fields = [
            'full_name',
            'email',
            'phone_number',
            'address_line_1',
            'address_line_2',
            'town_or_city',
            'postcode',
            'country',
        ]
        widgets = {
            'full_name': forms.HiddenInput(),
        }

    def save(self, commit=True):
        order = super().save(commit=False)

        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        order.full_name = f"{first_name} {last_name}".strip()

        if commit:
            order.save()

        return order
