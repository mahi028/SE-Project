<script setup>
import { notificationService } from '@/service/NotificationService';
import { onMounted, ref, computed } from 'vue';

const notificationsYesterday = ref(null);
const notificationsToday = ref(null);

onMounted(() => {
    notificationService.getNotifications().then((data) => {
        notificationsToday.value = data.today;
        notificationsYesterday.value = data.yesterday;
    });
});

const totalNotifications = computed(() => {
    return (notificationsToday.value?.length || 0) + (notificationsYesterday.value?.length || 0);
});

const getNotificationIcon = (type) => {
    switch (type) {
        case 'Appointment':
            return 'pi pi-calendar-clock';
        case 'Vital':
            return 'pi pi-heart';
        case 'Reminder':
            return 'pi pi-bell';
        default:
            return 'pi pi-info-circle';
    }
};

const getNotificationColor = (type) => {
    switch (type) {
        case 'Appointment':
            return 'blue';
        case 'Vital':
            return 'red';
        case 'Reminder':
            return 'green';
        default:
            return 'gray';
    }
};

const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
        case 'high':
            return 'text-red-600 dark:text-red-400';
        case 'normal':
            return 'text-green-600 dark:text-green-400';
        case 'low':
            return 'text-yellow-600 dark:text-yellow-400';
        default:
            return 'text-red-600 dark:text-red-400';
    }
};
</script>

<template>
    <div class="notifications-widget">
        <Card class="w-full h-full">
            <template #header>
                <div class="section-header">
                    <div class="flex items-center gap-2">
                        <i class="pi pi-bell text-blue-500"></i>
                        <h3 class="section-title">Notifications</h3>
                    </div>
                    <Badge
                        v-if="totalNotifications > 0"
                        :value="totalNotifications"
                        severity="info"
                        class="notification-badge"
                    />
                </div>
            </template>
            <template #content>
                <!-- TODAY SECTION -->
                <div v-if="notificationsToday && notificationsToday.length > 0" class="notification-section">
                    <div class="section-divider">
                        <span class="section-label">Today</span>
                        <Badge :value="notificationsToday.length" severity="info" />
                    </div>

                    <div class="notification-list">
                        <Card
                            v-for="(notification, index) in notificationsToday"
                            :key="`today-${index}`"
                            class="notification-item"
                        >
                            <template #content>
                                <div class="notification-content">
                                    <div :class="`notification-icon bg-${getNotificationColor(notification.type)}-100 dark:bg-${getNotificationColor(notification.type)}-900/20`">
                                        <i :class="`${getNotificationIcon(notification.type)} text-${getNotificationColor(notification.type)}-500`"></i>
                                    </div>

                                    <div class="notification-details">
                                        <div class="notification-text">
                                            <!-- Appointment -->
                                            <template v-if="notification.type === 'Appointment'">
                                                <span class="font-medium text-surface-900 dark:text-surface-0">
                                                    Dr. {{ notification.name }}
                                                </span>
                                                <p class="text-sm text-surface-600 dark:text-surface-400">
                                                    Appointment at {{ notification.time }}
                                                    <span class="font-semibold text-blue-600 dark:text-blue-400">
                                                        {{ notification.time_left }}
                                                    </span>
                                                </p>
                                            </template>

                                            <!-- Vital -->
                                            <template v-else-if="notification.type === 'Vital'">
                                                <span class="font-medium text-surface-900 dark:text-surface-0">
                                                    {{ notification.label }} Alert
                                                </span>
                                                <p class="text-sm text-surface-600 dark:text-surface-400">
                                                    Your {{ notification.label.toLowerCase() }} is
                                                    <span :class="getSeverityColor(notification.serverity)" class="font-semibold">
                                                        {{ notification.serverity }}
                                                    </span>
                                                </p>
                                            </template>

                                            <!-- Reminder -->
                                            <template v-else-if="notification.type === 'Reminder'">
                                                <span class="font-medium text-surface-900 dark:text-surface-0">
                                                    {{ notification.label }}
                                                </span>
                                                <p class="text-sm text-surface-600 dark:text-surface-400">
                                                    Scheduled for {{ notification.time }}
                                                </p>
                                            </template>
                                        </div>

                                        <div class="notification-actions">
                                            <Button
                                                v-if="notification.type === 'Vital'"
                                                label="View"
                                                size="small"
                                                text
                                                class="p-0"
                                            />
                                            <Button
                                                icon="pi pi-times"
                                                size="small"
                                                text
                                                rounded
                                                class="notification-dismiss"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </div>
                </div>

                <!-- YESTERDAY SECTION -->
                <div v-if="notificationsYesterday && notificationsYesterday.length > 0" class="notification-section">
                    <div class="section-divider">
                        <span class="section-label">Yesterday</span>
                        <Badge :value="notificationsYesterday.length" severity="secondary" />
                    </div>

                    <div class="notification-list">
                        <Card
                            v-for="(notification, index) in notificationsYesterday"
                            :key="`yesterday-${index}`"
                            class="notification-item yesterday"
                        >
                            <template #content>
                                <div class="notification-content">
                                    <div :class="`notification-icon bg-${getNotificationColor(notification.type)}-100 dark:bg-${getNotificationColor(notification.type)}-900/20 opacity-70`">
                                        <i :class="`${getNotificationIcon(notification.type)} text-${getNotificationColor(notification.type)}-500 opacity-70`"></i>
                                    </div>

                                    <div class="notification-details">
                                        <div class="notification-text">
                                            <!-- Appointment -->
                                            <template v-if="notification.type === 'Appointment'">
                                                <span class="font-medium text-surface-700 dark:text-surface-300">
                                                    Dr. {{ notification.name }}
                                                </span>
                                                <p class="text-sm text-surface-500 dark:text-surface-500">
                                                    Appointment at {{ notification.time }}
                                                    <span class="font-medium">
                                                        {{ notification.time_left }}
                                                    </span>
                                                </p>
                                            </template>

                                            <!-- Vital -->
                                            <template v-else-if="notification.type === 'Vital'">
                                                <span class="font-medium text-surface-700 dark:text-surface-300">
                                                    {{ notification.label }} Alert
                                                </span>
                                                <p class="text-sm text-surface-500 dark:text-surface-500">
                                                    Your {{ notification.label.toLowerCase() }} was
                                                    <span class="font-medium">
                                                        {{ notification.serverity }}
                                                    </span>
                                                </p>
                                            </template>

                                            <!-- Reminder -->
                                            <template v-else-if="notification.type === 'Reminder'">
                                                <span class="font-medium text-surface-700 dark:text-surface-300">
                                                    {{ notification.label }}
                                                </span>
                                                <p class="text-sm text-surface-500 dark:text-surface-500">
                                                    Was scheduled for {{ notification.time }}
                                                </p>
                                            </template>
                                        </div>

                                        <div class="notification-actions">
                                            <Button
                                                icon="pi pi-times"
                                                size="small"
                                                text
                                                rounded
                                                class="notification-dismiss opacity-50"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </div>
                </div>

                <!-- EMPTY STATE -->
                <div v-if="(!notificationsToday || notificationsToday.length === 0) && (!notificationsYesterday || notificationsYesterday.length === 0)" class="empty-state">
                    <div class="text-center py-8">
                        <div class="text-surface-400 dark:text-surface-500 mb-3">
                            <i class="pi pi-bell-slash text-4xl"></i>
                        </div>
                        <h4 class="text-lg font-medium text-surface-600 dark:text-surface-400 mb-2">
                            No Notifications
                        </h4>
                        <p class="text-sm text-surface-500 dark:text-surface-500">
                            You're all caught up! New notifications will appear here.
                        </p>
                    </div>
                </div>
            </template>
        </Card>
    </div>
</template>

<style scoped>
.notifications-widget {
    max-width: 100%;
    height: 100%;
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 1.5rem 0;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
}

.notification-badge {
    font-size: 0.75rem;
}

.notification-section {
    margin-bottom: 1.5rem;
}

.notification-section:last-child {
    margin-bottom: 0;
}

.section-divider {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--surface-border);
    margin-bottom: 1rem;
}

.section-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-color-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.notification-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.notification-item {
    transition: all 0.2s ease;
    border: 1px solid var(--surface-border);
    cursor: pointer;
}

.notification-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.notification-item.yesterday {
    opacity: 0.8;
}

.notification-content {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.5rem;
}

.notification-icon {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.notification-details {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
}

.notification-text {
    flex: 1;
}

.notification-actions {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    flex-shrink: 0;
}

.notification-dismiss {
    opacity: 0;
    transition: opacity 0.2s ease;
}

.notification-item:hover .notification-dismiss {
    opacity: 1;
}

.empty-state {
    background: var(--surface-ground);
    border-radius: 12px;
    border: 2px dashed var(--surface-border);
}

/* Dark mode enhancements */
:global(.p-dark) .notifications-widget :deep(.p-card) {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

/* Responsive design */
@media (max-width: 768px) {
    .section-header {
        padding: 1rem 1rem 0;
    }

    .notification-content {
        padding: 0.25rem;
    }

    .notification-icon {
        width: 2rem;
        height: 2rem;
    }
}

/* Animation for new notifications */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.notification-item {
    animation: slideIn 0.3s ease;
}
</style>
