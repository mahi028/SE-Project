<script setup>
import AppointmentRequests from '@/components/doctorDashboard/AppointmentRequests.vue';
import DoctorAppointments from '@/components/doctorDashboard/DoctorAppointments.vue';
import QuickButtons from '@/components/QuickButtons.vue';
import Divider from 'primevue/divider';
import { ref } from 'vue';

const value = ref('Appointments | Requests');
const options = ref(['Appointments | Requests']);
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <QuickButtons page="doctor"/>

        <div class="col-span-12 xl:col-span-12">
            <Divider align="left" type="solid">
                <h3>Quick Widgets</h3>
            </Divider>
        </div>
    </div>

    <!-- Responsive Widget Selector -->
    <div class="mb-6">
        <div class="card">
            <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <h4 class="text-lg font-semibold text-surface-700 dark:text-surface-300">Dashboard Widgets</h4>

                <!-- Mobile/Tablet: Dropdown -->
                <div class="lg:hidden w-full">
                    <Select
                        v-model="value"
                        :options="options"
                        placeholder="Select a Widget"
                        class="w-full"
                    />
                </div>

                <!-- Desktop: Button Group -->
                <div class="hidden lg:block">
                    <SelectButton
                        v-model="value"
                        :options="options"
                        class="responsive-select-button"
                    />
                </div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12 xl:col-span-6" v-show="value==='Appointments | Requests'">
            <DoctorAppointments />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value==='Appointments | Requests'">
            <AppointmentRequests />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value==='Notifications'">
            <DoctorNotificationsWidget />
        </div>
    </div>
</template>

<style scoped>
/* Responsive SelectButton styling */
:deep(.responsive-select-button .p-selectbutton) {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
}

:deep(.responsive-select-button .p-button) {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    max-width: 180px;
}

/* Mobile responsiveness */
@media (max-width: 1024px) {
    :deep(.responsive-select-button .p-button) {
        font-size: 0.75rem;
        padding: 0.375rem 0.5rem;
        max-width: 140px;
    }
}

@media (max-width: 640px) {
    .grid {
        gap: 1rem;
    }
}
</style>
