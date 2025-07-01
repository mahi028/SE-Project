<script setup>
import { notificationService } from '@/service/NotificationService';
import { onMounted, ref } from 'vue';

const notificationsYersterday = ref(null);
const notificationsToday = ref(null);

onMounted(() => {
    notificationService.getNotifications().then((data) => {notificationsToday.value = data.today;notificationsYersterday.value = data.yesterday});
});

</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-6">
            <div class="font-semibold text-xl">Notifications</div>
        </div>

        <!-- TODAY -->
        <span class="block text-muted-color font-medium mb-4">TODAY</span>
        <ul class="p-0 mx-0 mt-0 mb-6 list-none">
            <li class="flex items-center py-2 border-b border-surface" v-for="notification in notificationsToday || []">
                <!-- ICONS -->
                <div
                    class="w-12 h-12 flex items-center justify-center rounded-full mr-4 shrink-0"
                    :class="{
                        'bg-blue-100 dark:bg-blue-400/10': notification.type === 'Appointment',
                        'bg-red-100 dark:bg-red-400/10': notification.type === 'Vital',
                        'bg-green-100 dark:bg-green-400/10': notification.type === 'Reminder'
                    }"
                >
                    <i
                        class="!text-xl"
                        :class="{
                            'pi pi-calendar-clock text-blue-500': notification.type === 'Appointment',
                            'pi pi-heart text-red-500': notification.type === 'Vital',
                            'pi pi-bell text-green-500': notification.type === 'Reminder'
                        }"
                    ></i>
                </div>

                <!-- TEXT DETAILS -->
                <span class="text-surface-900 dark:text-surface-0 leading-normal">
                    <!-- Appointment -->
                    <template v-if="notification.type === 'Appointment'">
                        {{ notification.name }}'s
                        <span class="text-surface-700 dark:text-surface-100">
                            appointment at {{ notification.time }}
                            <span class="text-primary font-bold">{{ notification.time_left }}</span>
                        </span>
                    </template>

                    <!-- Vital -->
                    <template v-else-if="notification.type === 'Vital'">
                        {{ notification.name }}'s
                        <span class="text-surface-700 dark:text-surface-100">
                            {{ notification.label }} is
                            <span class="font-bold text-red-500">{{ notification.serverity }}</span>.
                            <span class="text-primary font-bold">View Here</span>
                        </span>
                    </template>

                    <!-- Reminder -->
                    <template v-else-if="notification.type === 'Reminder'">
                        <span class="text-surface-700 dark:text-surface-100">
                            Reminder: <span class="font-bold">{{ notification.label }}</span> at
                            <span class="text-primary font-bold">{{ notification.time }}</span>
                        </span>
                    </template>
                </span>
            </li>
        </ul>

        <!-- YESTERDAY -->
        <span class="block text-muted-color font-medium mb-4">YESTERDAY</span>
        <ul class="p-0 mx-0 mt-0 mb-6 list-none">
            <li class="flex items-center py-2 border-b border-surface" v-for="notification in notificationsYersterday || []">
                <!-- ICONS -->
                <div
                    class="w-12 h-12 flex items-center justify-center rounded-full mr-4 shrink-0"
                    :class="{
                        'bg-blue-100 dark:bg-blue-400/10': notification.type === 'Appointment',
                        'bg-red-100 dark:bg-red-400/10': notification.type === 'Vital',
                        'bg-green-100 dark:bg-green-400/10': notification.type === 'Reminder'
                    }"
                >
                    <i
                        class="!text-xl"
                        :class="{
                            'pi pi-calendar-clock text-blue-500': notification.type === 'Appointment',
                            'pi pi-heart text-red-500': notification.type === 'Vital',
                            'pi pi-bell text-green-500': notification.type === 'Reminder'
                        }"
                    ></i>
                </div>

                <!-- TEXT DETAILS -->
                <span class="text-surface-900 dark:text-surface-0 leading-normal">
                    <!-- Appointment -->
                    <template v-if="notification.type === 'Appointment'">
                        {{ notification.name }}'s
                        <span class="text-surface-700 dark:text-surface-100">
                            appointment at {{ notification.time }}
                            <span class="text-primary font-bold">{{ notification.time_left }}</span>
                        </span>
                    </template>

                    <!-- Vital -->
                    <template v-else-if="notification.type === 'Vital'">
                        {{ notification.name }}'s
                        <span class="text-surface-700 dark:text-surface-100">
                            {{ notification.label }} is
                            <span class="font-bold text-red-500">{{ notification.serverity }}</span>.
                            <span class="text-primary font-bold">View Here</span>
                        </span>
                    </template>

                    <!-- Reminder -->
                    <template v-else-if="notification.type === 'Reminder'">
                        <span class="text-surface-700 dark:text-surface-100">
                            Reminder: <span class="font-bold">{{ notification.label }}</span> at
                            <span class="text-primary font-bold">{{ notification.time }}</span>
                        </span>
                    </template>
                </span>
            </li>
        </ul>
    </div>
</template>