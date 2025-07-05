<script setup>
import { appointmentService } from '@/service/AppointmentService';
import { doctorService } from '@/service/DoctorService';
import { useLoginStore } from '@/store/loginStore';
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

const toast = useToast();
const confirm = useConfirm();
const appointments = ref([]);
const doctors = ref([]);
const loginStore = useLoginStore();
const loading = ref(false);

const fetchAppointments = async () => {
    loading.value = true;
    try {
        const data = await appointmentService.getAppointmentsBySenior(loginStore.ez_id);
        appointments.value = data;

        // Fetch doctor details for each appointment
        const doctorIds = [...new Set(data.map(apt => apt.doc_id))];
        const doctorPromises = doctorIds.map(id => doctorService.getDoctor({ ez_id: id }));
        const doctorData = await Promise.all(doctorPromises);
        doctors.value = doctorData.filter(doc => doc);
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to fetch appointments',
            life: 3000
        });
    } finally {
        loading.value = false;
    }
};

const getDoctorInfo = (docId) => {
    return doctors.value.find(doc => doc.ez_id === docId) || {};
};

const getAppointmentStatus = (date, time) => {
    const appointmentDateTime = new Date(`${date} ${time}`);
    const now = new Date();

    if (appointmentDateTime < now) {
        return { label: 'Completed', severity: 'success' };
    } else {
        const diffTime = appointmentDateTime - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays <= 1) {
            return { label: 'Today/Tomorrow', severity: 'warning' };
        } else {
            return { label: 'Upcoming', severity: 'info' };
        }
    }
};

const getSpecializationColor = (specialization) => {
    switch (specialization) {
        case 'Cardiologist':
            return 'danger';
        case 'Neurologist':
            return 'success';
        case 'Pediatrician':
            return 'info';
        case 'Gynecologist':
            return 'warning';
        case 'Orthopedist':
            return 'secondary';
        default:
            return 'primary';
    }
};

const upcomingAppointments = computed(() => {
    return appointments.value.filter(apt => {
        const appointmentDateTime = new Date(`${apt.date} ${apt.time}`);
        return appointmentDateTime >= new Date();
    }).sort((a, b) => new Date(`${a.date} ${a.time}`) - new Date(`${b.date} ${b.time}`));
});

const pastAppointments = computed(() => {
    return appointments.value.filter(apt => {
        const appointmentDateTime = new Date(`${apt.date} ${apt.time}`);
        return appointmentDateTime < new Date();
    }).sort((a, b) => new Date(`${b.date} ${b.time}`) - new Date(`${a.date} ${a.time}`));
});

const cancelAppointment = (appointment) => {
    const doctorInfo = getDoctorInfo(appointment.doc_id);
    confirm.require({
        message: `Are you sure you want to cancel your appointment with ${doctorInfo.name || appointment.doctorEmail?.split('@')[0]} on ${appointment.date} at ${appointment.time}?`,
        header: 'Cancel Appointment',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: {
            label: 'Keep Appointment',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Cancel Appointment',
            severity: 'danger'
        },
        accept: async () => {
            try {
                // Simulate API call to cancel appointment
                await new Promise(resolve => setTimeout(resolve, 500));

                // Remove appointment from list
                appointments.value = appointments.value.filter(apt =>
                    !(apt.doc_id === appointment.doc_id && apt.date === appointment.date && apt.time === appointment.time)
                );

                toast.add({
                    severity: 'success',
                    summary: 'Appointment Cancelled',
                    detail: 'Your appointment has been cancelled successfully.',
                    life: 3000
                });
            } catch (error) {
                toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to cancel appointment. Please try again.',
                    life: 3000
                });
            }
        }
    });
};

onMounted(() => {
    fetchAppointments();
});
</script>

<template>
    <Toast />
    <ConfirmDialog />
    <div class="appointments-card">
        <Card class="w-full">
            <template #header>
                <div class="section-header">
                    <i class="pi pi-calendar text-blue-500"></i>
                    <h3 class="section-title">My Appointments</h3>
                </div>
            </template>
            <template #content>
                <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                    <p class="text-surface-600 dark:text-surface-400">
                        Keep track of your medical appointments and consultations.
                    </p>
                    <Button
                        icon="pi pi-refresh"
                        outlined
                        @click="fetchAppointments"
                        v-tooltip.top="'Refresh appointments'"
                        :loading="loading"
                    />
                </div>

                <div v-if="loading" class="text-center py-8">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                </div>

                <div v-else-if="appointments.length === 0" class="empty-state">
                    <div class="text-center py-12">
                        <div class="text-surface-400 dark:text-surface-500 mb-4">
                            <i class="pi pi-calendar-times text-6xl"></i>
                        </div>
                        <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                            No Appointments Found
                        </h4>
                        <p class="text-surface-500 dark:text-surface-400 mb-4">
                            You haven't booked any appointments yet.
                        </p>
                    </div>
                </div>

                <div v-else class="appointments-content">
                    <!-- Upcoming Appointments -->
                    <div v-if="upcomingAppointments.length > 0" class="appointment-section">
                        <div class="section-divider">
                            <span class="section-label">Upcoming Appointments</span>
                            <Badge :value="upcomingAppointments.length" severity="info" />
                        </div>

                        <div class="appointment-list">
                            <Card
                                v-for="appointment in upcomingAppointments"
                                :key="appointment.appointment_id"
                                class="appointment-item upcoming"
                            >
                                <template #content>
                                    <div class="appointment-content">
                                        <div class="appointment-doctor">
                                            <div class="doctor-avatar">
                                                <i class="pi pi-user-md text-blue-500"></i>
                                            </div>
                                            <div class="doctor-info">
                                                <h4 class="doctor-name">{{ getDoctorInfo(appointment.doc_id).name || 'Dr. ' + appointment.doctorEmail?.split('@')[0] }}</h4>
                                                <p class="doctor-specialization">{{ getDoctorInfo(appointment.doc_id).specialization || 'General Medicine' }}</p>
                                                <div class="doctor-hospital">
                                                    <i class="pi pi-building text-surface-500 dark:text-surface-400"></i>
                                                    <span class="text-surface-700 dark:text-surface-300">{{ getDoctorInfo(appointment.doc_id).hospital || 'Medical Center' }}</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="appointment-details">
                                            <div class="appointment-datetime">
                                                <div class="date-info">
                                                    <i class="pi pi-calendar text-green-500"></i>
                                                    <span class="font-medium">{{ appointment.date }}</span>
                                                </div>
                                                <div class="time-info">
                                                    <i class="pi pi-clock text-orange-500"></i>
                                                    <span class="font-medium">{{ appointment.time }}</span>
                                                </div>
                                            </div>

                                            <div class="appointment-reason" v-if="appointment.reason">
                                                <i class="pi pi-file-text text-surface-500 dark:text-surface-400"></i>
                                                <span class="text-surface-700 dark:text-surface-300">{{ appointment.reason }}</span>
                                            </div>
                                        </div>

                                        <div class="appointment-actions">
                                            <Tag
                                                :value="getAppointmentStatus(appointment.date, appointment.time).label"
                                                :severity="getAppointmentStatus(appointment.date, appointment.time).severity"
                                                class="mb-2"
                                            />
                                            <div class="action-buttons">
                                                <Button
                                                    icon="pi pi-eye"
                                                    label="View Doctor"
                                                    size="small"
                                                    outlined
                                                    v-tooltip.top="'View Doctor Profile'"
                                                    as="router-link"
                                                    :to="`/doctor/${appointment.doc_id}`"
                                                    class="w-full mb-2"
                                                />
                                                <div class="flex gap-2">
                                                    <Button
                                                        icon="pi pi-phone"
                                                        size="small"
                                                        outlined
                                                        v-tooltip.top="'Call Doctor'"
                                                        :href="`tel:${getDoctorInfo(appointment.doc_id).phone || ''}`"
                                                    />
                                                    <Button
                                                        icon="pi pi-times"
                                                        size="small"
                                                        severity="danger"
                                                        outlined
                                                        v-tooltip.top="'Cancel Appointment'"
                                                        @click="cancelAppointment(appointment)"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </Card>
                        </div>
                    </div>

                    <!-- Past Appointments - no cancel button needed -->
                    <div v-if="pastAppointments.length > 0" class="appointment-section">
                        <div class="section-divider">
                            <span class="section-label">Past Appointments</span>
                            <Badge :value="pastAppointments.length" severity="secondary" />
                        </div>

                        <div class="appointment-list">
                            <Card
                                v-for="appointment in pastAppointments.slice(0, 5)"
                                :key="appointment.appointment_id"
                                class="appointment-item past"
                            >
                                <template #content>
                                    <div class="appointment-content">
                                        <div class="appointment-doctor">
                                            <div class="doctor-avatar opacity-70">
                                                <i class="pi pi-user-md text-surface-500"></i>
                                            </div>
                                            <div class="doctor-info">
                                                <h4 class="doctor-name text-surface-800 dark:text-surface-200">{{ getDoctorInfo(appointment.doc_id).name || 'Dr. ' + appointment.doctorEmail?.split('@')[0] }}</h4>
                                                <p class="doctor-specialization text-surface-600 dark:text-surface-400">{{ getDoctorInfo(appointment.doc_id).specialization || 'General Medicine' }}</p>
                                                <div class="doctor-hospital">
                                                    <i class="pi pi-building text-surface-500 dark:text-surface-400"></i>
                                                    <span class="text-surface-600 dark:text-surface-400">{{ getDoctorInfo(appointment.doc_id).hospital || 'Medical Center' }}</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="appointment-details">
                                            <div class="appointment-datetime">
                                                <div class="date-info">
                                                    <i class="pi pi-calendar text-surface-400"></i>
                                                    <span class="text-surface-600 dark:text-surface-400">{{ appointment.date }}</span>
                                                </div>
                                                <div class="time-info">
                                                    <i class="pi pi-clock text-surface-400"></i>
                                                    <span class="text-surface-600 dark:text-surface-400">{{ appointment.time }}</span>
                                                </div>
                                            </div>

                                            <div class="appointment-reason" v-if="appointment.reason">
                                                <i class="pi pi-file-text text-surface-500 dark:text-surface-400"></i>
                                                <span class="text-surface-600 dark:text-surface-400">{{ appointment.reason }}</span>
                                            </div>
                                        </div>

                                        <div class="appointment-actions">
                                            <Tag
                                                :value="getAppointmentStatus(appointment.date, appointment.time).label"
                                                :severity="getAppointmentStatus(appointment.date, appointment.time).severity"
                                                class="mb-2"
                                            />
                                            <div class="action-buttons">
                                                <Button
                                                    icon="pi pi-eye"
                                                    label="View"
                                                    size="small"
                                                    outlined
                                                    v-tooltip.top="'View Doctor Profile'"
                                                    as="router-link"
                                                    :to="`/doctor/${appointment.doc_id}`"
                                                    class="w-full"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </Card>
                        </div>

                        <div v-if="pastAppointments.length > 5" class="text-center mt-4">
                            <Button
                                label="View All Past Appointments"
                                icon="pi pi-history"
                                text
                            />
                        </div>
                    </div>
                </div>
            </template>
        </Card>
    </div>
</template>

<style scoped>
.appointments-card {
    max-width: 100%;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem 1.5rem 0;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
}

.empty-state {
    background: var(--surface-ground);
    border-radius: 12px;
    border: 2px dashed var(--surface-border);
}

.appointment-section {
    margin-bottom: 2rem;
}

.appointment-section:last-child {
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

.appointment-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.appointment-item {
    transition: all 0.2s ease;
    border: 1px solid var(--surface-border);
    cursor: pointer;
}

.appointment-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.appointment-item.upcoming {
    border-left: 4px solid var(--primary-500);
}

.appointment-item.past {
    opacity: 0.8;
    border-left: 4px solid var(--surface-300);
}

.appointment-content {
    display: grid;
    grid-template-columns: 2fr 2fr 1fr;
    gap: 1rem;
    align-items: start;
    padding: 1rem;
}

.appointment-doctor {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.doctor-avatar {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: var(--primary-100);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

:global(.p-dark) .doctor-avatar {
    background: var(--primary-900);
}

.doctor-info {
    flex: 1;
}

.doctor-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 0.25rem 0;
}

.doctor-specialization {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
    margin: 0 0 0.5rem 0;
    font-weight: 500;
}

.doctor-hospital {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 500;
}

.appointment-details {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.appointment-datetime {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.date-info,
.time-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
}

.appointment-reason {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text-color-secondary);
}

.appointment-actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
}

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* Dark mode enhancements */
:global(.p-dark) .appointments-card :deep(.p-card) {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

/* Responsive design */
@media (max-width: 768px) {
    .section-header {
        padding: 1rem 1rem 0;
    }

    .appointment-content {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .appointment-actions {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }

    .action-buttons {
        flex-direction: row;
    }
}

/* Animation for new appointments */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.appointment-item {
    animation: slideIn 0.3s ease;
}
.appointment-item {
    animation: slideIn 0.3s ease;
}
</style>
