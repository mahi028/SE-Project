<script setup>
import { ref, computed, watch } from 'vue';
import { useQuery } from '@vue/apollo-composable';
import { useToast } from 'primevue/usetoast';
import gql from 'graphql-tag';

const toast = useToast();

// GraphQL query
const GET_USER_NOTIFICATIONS = gql`
    query GetUserNotifications {
        getUserNotifications {
            notId
            ezId
            label
            time
            category
        }
    }
`;

// Category mapping
const CATEGORY_MAP = {
    0: 'Appointment',
    1: 'Reminder', // Medic
    2: 'Reminder', // Hydration
    3: 'Reminder', // Group
    4: 'Reminder', // Exercise
    5: 'Reminder', // Diet
    6: 'Reminder', // Sleep
};

// Execute GraphQL query
const { result, loading, error, refetch } = useQuery(GET_USER_NOTIFICATIONS, null, {
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all'
});

// Reactive data
const notificationsToday = ref([]);
const notificationsYesterday = ref([]);

// Helper functions
const formatNotificationTime = (timeString) => {
    if (!timeString) return 'Unknown time';

    try {
        const date = new Date(timeString);
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    } catch (error) {
        console.error('Error formatting time:', error);
        return 'Unknown time';
    }
};

const calculateTimeLeft = (timeString) => {
    if (!timeString) return null;

    try {
        const appointmentTime = new Date(timeString);
        const now = new Date();
        const diffMs = appointmentTime.getTime() - now.getTime();

        if (diffMs <= 0) return 'Past due';

        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

        if (diffHours > 0) {
            return `in ${diffHours}h ${diffMinutes}m`;
        } else {
            return `in ${diffMinutes}m`;
        }
    } catch (error) {
        console.error('Error calculating time left:', error);
        return null;
    }
};

const transformNotificationData = (notifications) => {
    if (!notifications || !Array.isArray(notifications)) return [];

    return notifications.map(notification => {
        const type = CATEGORY_MAP[notification.category] || 'Reminder';
        const baseNotification = {
            id: notification.notId,
            type: type,
            label: notification.label,
            time: formatNotificationTime(notification.time),
            category: notification.category,
            rawTime: notification.time
        };

        // Add type-specific properties
        if (type === 'Appointment') {
            // Extract doctor name from appointment label (assuming format like "Appointment with Dr. Name")
            const doctorMatch = notification.label.match(/(?:with\s+)?Dr\.\s*([^,\n]+)/i);
            baseNotification.name = doctorMatch ? doctorMatch[1].trim() : 'Unknown Doctor';
            baseNotification.time_left = calculateTimeLeft(notification.time);
        } else if (type === 'Vital') {
            // For vital notifications, assume high severity if not specified
            baseNotification.severity = 'high';
        }

        return baseNotification;
    });
};

const categorizeNotificationsByDate = (notifications) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const todayNotifications = [];
    const yesterdayNotifications = [];

    notifications.forEach(notification => {
        if (!notification.rawTime) {
            todayNotifications.push(notification);
            return;
        }

        const notificationDate = new Date(notification.rawTime);
        const isToday = notificationDate.toDateString() === today.toDateString();
        const isYesterday = notificationDate.toDateString() === yesterday.toDateString();

        if (isToday) {
            todayNotifications.push(notification);
        } else if (isYesterday) {
            yesterdayNotifications.push(notification);
        }
    });

    return {
        today: todayNotifications,
        yesterday: yesterdayNotifications
    };
};

// Process notifications when data changes
const processNotifications = () => {
    if (result.value?.getUserNotifications) {
        const transformedNotifications = transformNotificationData(result.value.getUserNotifications);
        const categorized = categorizeNotificationsByDate(transformedNotifications);

        notificationsToday.value = categorized.today;
        notificationsYesterday.value = categorized.yesterday;
    } else {
        notificationsToday.value = [];
        notificationsYesterday.value = [];
    }
};

// Watch for result changes
watch(result, processNotifications, { immediate: true });

// Handle errors
watch(error, (newError) => {
    if (newError) {
        console.error('GraphQL Error:', newError);
        toast.add({
            severity: 'error',
            summary: 'Error Loading Notifications',
            detail: 'Failed to load notifications. Please try again.',
            life: 5000
        });
    }
});

// Computed properties
const totalNotifications = computed(() => {
    return (notificationsToday.value?.length || 0) + (notificationsYesterday.value?.length || 0);
});

// Helper functions for UI
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

// Actions
const refreshNotifications = async () => {
    try {
        await refetch();
        toast.add({
            severity: 'success',
            summary: 'Refreshed',
            detail: 'Notifications updated successfully.',
            life: 3000
        });
    } catch (err) {
        toast.add({
            severity: 'error',
            summary: 'Refresh Failed',
            detail: 'Failed to refresh notifications.',
            life: 3000
        });
    }
};

const dismissNotification = (notificationId) => {
    // For now, just show a toast. Later this can be connected to a mutation
    toast.add({
        severity: 'info',
        summary: 'Notification Dismissed',
        detail: 'This notification has been dismissed.',
        life: 3000
    });

    // Remove from local arrays
    notificationsToday.value = notificationsToday.value.filter(n => n.id !== notificationId);
    notificationsYesterday.value = notificationsYesterday.value.filter(n => n.id !== notificationId);
};
</script>

<template>
    <Toast />
    <div class="notifications-widget">
        <Card class="w-full h-full">
            <template #header>
                <div class="section-header">
                    <div class="flex items-center gap-2">
                        <i class="pi pi-bell text-blue-500"></i>
                        <h3 class="section-title">Notifications</h3>
                    </div>
                    <div class="flex items-center gap-2">
                        <Badge
                            v-if="totalNotifications > 0"
                            :value="totalNotifications"
                            severity="info"
                            class="notification-badge"
                        />
                        <Button
                            icon="pi pi-refresh"
                            size="small"
                            text
                            rounded
                            @click="refreshNotifications"
                            :loading="loading"
                            v-tooltip.top="'Refresh notifications'"
                        />
                    </div>
                </div>
            </template>
            <template #content>
                <!-- Loading state -->
                <div v-if="loading" class="text-center py-8">
                    <ProgressSpinner style="width: 40px; height: 40px" strokeWidth="6" />
                    <p class="mt-3 text-surface-600 dark:text-surface-400">Loading notifications...</p>
                </div>

                <!-- Error state -->
                <div v-else-if="error" class="text-center py-8">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                    <p class="text-red-600 dark:text-red-400 mb-3">Failed to load notifications</p>
                    <Button label="Retry" @click="refetch" size="small" />
                </div>

                <!-- Content -->
                <div v-else>
                    <!-- TODAY SECTION -->
                    <div v-if="notificationsToday && notificationsToday.length > 0" class="notification-section">
                        <div class="section-divider">
                            <span class="section-label">Today</span>
                            <Badge :value="notificationsToday.length" severity="info" />
                        </div>

                        <div class="notification-list">
                            <Card
                                v-for="(notification, index) in notificationsToday"
                                :key="`today-${notification.id || index}`"
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
                                                        <span v-if="notification.time_left" class="font-semibold text-blue-600 dark:text-blue-400">
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
                                                        <span :class="getSeverityColor(notification.severity)" class="font-semibold">
                                                            {{ notification.severity }}
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
                                                    @click="dismissNotification(notification.id)"
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
                                :key="`yesterday-${notification.id || index}`"
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
                                                        <span v-if="notification.time_left" class="font-medium">
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
                                                            {{ notification.severity }}
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
                                                    @click="dismissNotification(notification.id)"
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
                            <p class="text-sm text-surface-500 dark:text-surface-500 mb-4">
                                You're all caught up! New notifications will appear here.
                            </p>
                            <Button
                                label="Refresh"
                                icon="pi pi-refresh"
                                size="small"
                                outlined
                                @click="refreshNotifications"
                            />
                        </div>
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
