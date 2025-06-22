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
        <span class="block text-muted-color font-medium mb-4">TODAY</span>
        <ul class="p-0 mx-0 mt-0 mb-6 list-none">
            <li class="flex items-center py-2 border-b border-surface" v-for="notification in notificationsToday || []">
                <div class="w-12 h-12 flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-full mr-4 shrink-0" v-if="notification.type == 'Appointment'">
                    <i class="pi pi-calendar-clock !text-xl text-blue-500"></i>
                </div>
                <div class="w-12 h-12 flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-full mr-4 shrink-0" v-else-if="notification.type == 'Vital'">
                    <i class="pi pi-heart !text-xl text-red-500"></i>
                </div>
                <!-- Appointment Notification -->
                <span class="text-surface-900 dark:text-surface-0 leading-normal"
                    v-if="notification.type == 'Appointment'"
                    >{{ notification.name }}'s
                    <span class="text-surface-700 dark:text-surface-100">appointment at {{ notification.time }} <span class="text-primary font-bold">{{ notification.time_left }}</span></span>
                </span>
                <!-- Vital Notification -->
                <span class="text-surface-900 dark:text-surface-0 leading-normal"
                    v-else-if="notification.type == 'Vital'"
                    >{{ notification.name }}'s
                    <span class="text-surface-700 dark:text-surface-100">{{ notification.label }} is <span class="font-bold" style="color: red;">{{ notification.serverity }}</span>. <span class="text-primary font-bold">View Here</span></span>
                </span>
            </li>
        </ul>

        <span class="block text-muted-color font-medium mb-4">YESTERDAY</span>
        <ul class="p-0 mx-0 mt-0 mb-6 list-none">
            <li class="flex items-center py-2 border-b border-surface" v-for="notification in notificationsYersterday || []">
                <div class="w-12 h-12 flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-full mr-4 shrink-0" v-if="notification.type == 'Appointment'">
                    <i class="pi pi-calendar-clock !text-xl text-blue-500"></i>
                </div>
                <div class="w-12 h-12 flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-full mr-4 shrink-0" v-else-if="notification.type == 'Vital'">
                    <i class="pi pi-heart !text-xl text-red-500"></i>
                </div>
                <!-- Appointment Notification -->
                <span class="text-surface-900 dark:text-surface-0 leading-normal"
                    v-if="notification.type == 'Appointment'"
                    >{{ notification.name }}'s
                    <span class="text-surface-700 dark:text-surface-100">appointment at {{ notification.time }} <span class="text-primary font-bold">{{ notification.time_left }}</span></span>
                </span>
                <!-- Vital Notification -->
                <span class="text-surface-900 dark:text-surface-0 leading-normal"
                    v-else-if="notification.type == 'Vital'"
                    >{{ notification.name }}'s
                    <span class="text-surface-700 dark:text-surface-100">{{ notification.label }} is <span class="font-bold" style="color: red;">{{ notification.serverity }}</span>. <span class="text-primary font-bold">View Here</span></span>
                </span>
            </li>
        </ul>
    </div>
</template>
