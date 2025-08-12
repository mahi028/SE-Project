<script setup>
import { ref, onMounted, computed } from 'vue';
import { useQuery, useMutation } from '@vue/apollo-composable';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import gql from 'graphql-tag';

const toast = useToast();
const confirm = useConfirm();
const loading = ref(false);

// GraphQL queries and mutations
const GET_APPOINTMENTS_FOR_DOCTOR = gql`
    query GetAppointmentsForDoctor {
        getAppointmentsForDoctor {
            appId
            senId
            docId
            remTime
            reason
            status
            createdAt
            senInfo {
                senId
                ezId
                gender
                address
                alternatePhoneNum
                user {
                    name
                    email
                    phoneNum
                    profileImageUrl
                }
            }
        }
    }
`;

const CANCEL_APPOINTMENT = gql`
    mutation CancelAppointment($appId: Int!) {
        cancelAppointment(appId: $appId) {
            message
            status
        }
    }
`;

// Apollo composables
const { result, loading: queryLoading, error, refetch } = useQuery(GET_APPOINTMENTS_FOR_DOCTOR);
const { mutate: cancelAppointmentMutation } = useMutation(CANCEL_APPOINTMENT);

// Filter appointments with status 1 (confirmed/accepted)
const appointments = computed(() => {
    const allAppointments = result.value?.getAppointmentsForDoctor || [];
    return allAppointments
        .filter(appointment => appointment.status === 1)
        .map(appointment => ({
            appointment_id: appointment.appId,
            sen_id: appointment.senInfo?.ezId,
            seniorName: appointment.senInfo?.user?.name || 'Unknown Patient',
            seniorEmail: appointment.senInfo?.user?.email || 'No email provided',
            seniorPhone: appointment.senInfo?.user?.phoneNum || appointment.senInfo?.alternatePhoneNum,
            seniorProfile: appointment.senInfo?.user?.profileImageUrl,
            date: new Date(appointment.remTime).toLocaleDateString(),
            time: new Date(appointment.remTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            reason: appointment.reason || 'General consultation',
            address: appointment.senInfo?.address,
            gender: appointment.senInfo?.gender,
            remTime: appointment.remTime
        }))
        .sort((a, b) => new Date(a.remTime) - new Date(b.remTime));
});

const getSeniorInfo = (senId) => {
    const appointment = appointments.value.find(apt => apt.sen_id === senId);
    return {
        name: appointment?.seniorName,
        phone: appointment?.seniorPhone,
        email: appointment?.seniorEmail
    };
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

const upcomingAppointments = computed(() => {
    return appointments.value.filter(apt => {
        const appointmentDateTime = new Date(apt.remTime);
        return appointmentDateTime >= new Date();
    });
});

const pastAppointments = computed(() => {
    return appointments.value.filter(apt => {
        const appointmentDateTime = new Date(apt.remTime);
        return appointmentDateTime < new Date();
    }).sort((a, b) => new Date(b.remTime) - new Date(a.remTime));
});

const cancelAppointment = (appointment) => {
    confirm.require({
        message: `Are you sure you want to cancel the appointment with ${appointment.seniorName} on ${appointment.date} at ${appointment.time}?`,
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
                const { data } = await cancelAppointmentMutation({
                    appId: appointment.appointment_id
                });

                const response = data?.cancelAppointment;
                if (response?.status === 1) {
                    toast.add({
                        severity: 'success',
                        summary: 'Appointment Cancelled',
                        detail: response.message || 'The appointment has been cancelled successfully.',
                        life: 3000
                    });

                    // Refetch appointments to update the list
                    await refetch();
                } else {
                    toast.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: response?.message || 'Failed to cancel appointment. Please try again.',
                        life: 3000
                    });
                }
            } catch (error) {
                console.error('Error cancelling appointment:', error);
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

const fetchAppointments = async () => {
    loading.value = true;
    try {
        await refetch();
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

onMounted(() => {
    // Data is automatically fetched by useQuery
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
                    <h3 class="section-title">My Confirmed Appointments</h3>
                </div>
            </template>
            <template #content>
                <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                    <p class="text-surface-600 dark:text-surface-400">
                        Manage your confirmed patient appointments and consultations.
                    </p>
                    <Button
                        icon="pi pi-refresh"
                        outlined
                        @click="fetchAppointments"
                        v-tooltip.top="'Refresh appointments'"
                        :loading="queryLoading || loading"
                    />
                </div>

                <!-- Loading state -->
                <div v-if="queryLoading" class="text-center py-8">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                    <p class="mt-4">Loading appointments...</p>
                </div>

                <!-- Error state -->
                <div v-else-if="error" class="text-center py-8">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                    <p class="text-red-600">Failed to load appointments</p>
                    <Button label="Retry" @click="refetch" class="mt-3" />
                </div>

                <!-- Empty state -->
                <div v-else-if="appointments.length === 0" class="empty-state">
                    <div class="text-center py-12">
                        <div class="text-surface-400 dark:text-surface-500 mb-4">
                            <i class="pi pi-calendar-times text-6xl"></i>
                        </div>
                        <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                            No Confirmed Appointments
                        </h4>
                        <p class="text-surface-500 dark:text-surface-400 mb-4">
                            You don't have any confirmed appointments scheduled yet.
                        </p>
                    </div>
                </div>

                <!-- Appointments content -->
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
                                        <div class="appointment-patient">
                                            <div class="patient-avatar">
                                                <Avatar
                                                    v-if="appointment.seniorProfile"
                                                    :image="appointment.seniorProfile"
                                                    shape="circle"
                                                    size="large"
                                                />
                                                <Avatar
                                                    v-else
                                                    :label="appointment.seniorName?.charAt(0) || 'P'"
                                                    shape="circle"
                                                    size="large"
                                                    class="bg-green-500 text-white"
                                                />
                                            </div>
                                            <div class="patient-info">
                                                <h4 class="patient-name">{{ appointment.seniorName }}</h4>
                                                <p class="patient-email">{{ appointment.seniorEmail }}</p>
                                                <div class="patient-phone" v-if="appointment.seniorPhone">
                                                    <i class="pi pi-phone text-surface-500 dark:text-surface-400"></i>
                                                    <span class="text-surface-700 dark:text-surface-300">{{ appointment.seniorPhone }}</span>
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
                                                    label="View"
                                                    size="small"
                                                    outlined
                                                    v-tooltip.top="'View Patient Profile'"
                                                    as="router-link"
                                                    :to="`/senior/${appointment.sen_id}`"
                                                    class="w-full mb-2"
                                                />
                                                <div class="flex gap-2">
                                                    <Button
                                                        icon="pi pi-phone"
                                                        size="small"
                                                        outlined
                                                        v-tooltip.top="'Call Patient'"
                                                        :href="`tel:${appointment.seniorPhone || ''}`"
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

                    <!-- Past Appointments -->
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
                                        <div class="appointment-patient">
                                            <div class="patient-avatar opacity-70">
                                                <Avatar
                                                    v-if="appointment.seniorProfile"
                                                    :image="appointment.seniorProfile"
                                                    shape="circle"
                                                    size="large"
                                                    class="opacity-70"
                                                />
                                                <Avatar
                                                    v-else
                                                    :label="appointment.seniorName?.charAt(0) || 'P'"
                                                    shape="circle"
                                                    size="large"
                                                    class="bg-surface-500 text-white"
                                                />
                                            </div>
                                            <div class="patient-info">
                                                <h4 class="patient-name text-surface-800 dark:text-surface-200">{{ appointment.seniorName }}</h4>
                                                <p class="patient-email text-surface-600 dark:text-surface-400">{{ appointment.seniorEmail }}</p>
                                                <div class="patient-phone" v-if="appointment.seniorPhone">
                                                    <i class="pi pi-phone text-surface-500 dark:text-surface-400"></i>
                                                    <span class="text-surface-600 dark:text-surface-400">{{ appointment.seniorPhone }}</span>
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
                                                    v-tooltip.top="'View Patient Profile'"
                                                    as="router-link"
                                                    :to="`/senior/${appointment.sen_id}`"
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

.appointment-patient {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.patient-avatar {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: var(--primary-100);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

:global(.p-dark) .patient-avatar {
    background: var(--primary-900);
}

.patient-info {
    flex: 1;
}

.patient-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 0.25rem 0;
}

.patient-email {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
    margin: 0 0 0.5rem 0;
    font-weight: 500;
}

.patient-phone {
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
</style>
