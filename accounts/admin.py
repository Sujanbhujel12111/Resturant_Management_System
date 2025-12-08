from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Staff

User = get_user_model()


class StaffInline(admin.StackedInline):
	model = Staff
	can_delete = False
	verbose_name_plural = 'staff profile'
	fk_name = 'user'
	extra = 0
	fields = ('role', 'contact', 'salary', 'joined_date', 'is_active')


class UserAdmin(BaseUserAdmin):
	inlines = (StaffInline,)

	def get_inline_instances(self, request, obj=None):
		if not obj:
			return []
		return super().get_inline_instances(request, obj)


from django.contrib.admin.sites import NotRegistered

try:
	admin.site.unregister(User)
except NotRegistered:
	# If the model wasn't registered yet (custom user setups), ignore
	pass

admin.site.register(User, UserAdmin)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
	list_display = ('user', 'role', 'is_active')
	search_fields = ('user__username', 'user__email', 'role')
	list_filter = ('is_active', 'role')
