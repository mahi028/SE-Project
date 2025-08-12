<script setup>
import { ref, onMounted, computed } from 'vue';
import { useQuery, useMutation } from '@vue/apollo-composable';
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";
import gql from 'graphql-tag';

const toast = useToast();
const confirm = useConfirm();
const visible = ref(false);
const selectedAppointment = ref(null);

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

const UPDATE_APPOINTMENT_STATUS = gql`
    mutation UpdateAppointmentStatus($appId: Int!, $status: Int!) {
        updateAppointmentStatus(appId: $appId, status: $status) {
            message
            status
        }
    }
`;

// Apollo composables
const { result, loading, error, refetch } = useQuery(GET_APPOINTMENTS_FOR_DOCTOR);
const { mutate: updateAppointmentStatus } = useMutation(UPDATE_APPOINTMENT_STATUS);

// Filter appointments with status 0 (pending)
const appointmentRequests = computed(() => {
    const appointments = result.value?.getAppointmentsForDoctor || [];
    return appointments
        .filter(appointment => appointment.status === 0)
        .map(appointment => ({
            appId: appointment.appId,
            sen_id: appointment.senInfo?.ezId,
            name: appointment.senInfo?.user?.name || 'Unknown Patient',
            email: appointment.senInfo?.user?.email || 'No email provided',
            phone: appointment.senInfo?.user?.phoneNum || appointment.senInfo?.alternatePhoneNum,
            profile: appointment.senInfo?.user?.profileImageUrl,
            date: new Date(appointment.remTime).toLocaleDateString(),
            time: new Date(appointment.remTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            reason: appointment.reason || 'General consultation',
            address: appointment.senInfo?.address,
            gender: appointment.senInfo?.gender,
            createdAt: new Date(appointment.createdAt).toLocaleDateString()
        }))
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)); // Sort by newest first
});

const displayAppointment = (appointment) => {
    selectedAppointment.value = appointment;
    visible.value = true;
}

const confirmAcceptRequest = (event) => {
    confirm.require({
        target: event.currentTarget,
        message: 'Are you sure you want to accept this appointment request?',
        icon: 'pi pi-check-circle',
        rejectProps: {
            label: 'Cancel',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Accept',
            severity: 'success'
        },
        accept: async () => {
            try {
                const { data } = await updateAppointmentStatus({
                    appId: selectedAppointment.value.appId,
                    status: 1 // confirmed
                });

                const response = data?.updateAppointmentStatus;
                if (response?.status === 200) {
                    toast.add({ 
                        severity: 'success', 
                        summary: 'Accepted', 
                        detail: response.message || 'Appointment request has been accepted', 
                        life: 3000 
                    });
                    
                    // Refetch appointments to update the list
                    await refetch();
                    visible.value = false;
                    selectedAppointment.value = null;
                } else {
                    toast.add({ 
                        severity: 'error', 
                        summary: 'Error', 
                        detail: response?.message || 'Failed to accept appointment', 
                        life: 3000 
                    });
                }
            } catch (error) {
                console.error('Error accepting appointment:', error);
                toast.add({ 
                    severity: 'error', 
                    summary: 'Error', 
                    detail: 'Failed to accept appointment. Please try again.', 
                    life: 3000 
                });
            }
        },
    });
};

const confirmRejectRequest = (event) => {
    confirm.require({
        target: event.currentTarget,
        message: 'Do you want to reject this appointment request?',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: {
            label: 'Cancel',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Reject',
            severity: 'danger'
        },
        accept: async () => {
            try {
                const { data } = await updateAppointmentStatus({
                    appId: selectedAppointment.value.appId,
                    status: -1 // rejected
                });

                const response = data?.updateAppointmentStatus;
                if (response?.status === 200) {
                    toast.add({ 
                        severity: 'info', 
                        summary: 'Rejected', 
                        detail: response.message || 'Appointment request has been rejected', 
                        life: 3000 
                    });
                    
                    // Refetch appointments to update the list
                    await refetch();
                    visible.value = false;
                    selectedAppointment.value = null;
                } else {
                    toast.add({ 
                        severity: 'error', 
                        summary: 'Error', 
                        detail: response?.message || 'Failed to reject appointment', 
                        life: 3000 
                    });
                }
            } catch (error) {
                console.error('Error rejecting appointment:', error);
                toast.add({ 
                    severity: 'error', 
                    summary: 'Error', 
                    detail: 'Failed to reject appointment. Please try again.', 
                    life: 3000 
                });
            }
        },
    });
};

onMounted(() => {
    // Data is automatically fetched by useQuery
});
</script>

<template>
    <Toast />
    <ConfirmPopup></ConfirmPopup>
    <div class="appointment-requests-card">
        <Card class="w-full">
            <template #header>
                <div class="section-header">
                    <i class="pi pi-inbox text-orange-500"></i>
                    <h3 class="section-title">Appointment Requests</h3>
                </div>
            </template>
            <template #content>
                <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                    <p class="text-surface-600 dark:text-surface-400">
                        Review and manage incoming appointment requests from patients.
                    </p>
                    <Button 
                        icon="pi pi-refresh" 
                        outlined
                        @click="refetch"
                        v-tooltip.top="'Refresh requests'"
                        :loading="loading"
                    />
                </div>

                <!-- Loading state -->
                <div v-if="loading" class="text-center py-8">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                    <p class="mt-4">Loading appointment requests...</p>
                </div>

                <!-- Error state -->
                <div v-else-if="error" class="text-center py-8">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                    <p class="text-red-600">Failed to load appointment requests</p>
                    <Button label="Retry" @click="refetch" class="mt-3" />
                </div>

                <!-- Empty state -->
                <div v-else-if="!appointmentRequests || appointmentRequests.length === 0" class="empty-state">
                    <div class="text-center py-12">
                        <div class="text-surface-400 dark:text-surface-500 mb-4">
                            <i class="pi pi-inbox text-6xl"></i>
                        </div>
                        <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                            No Appointment Requests
                        </h4>
                        <p class="text-surface-500 dark:text-surface-400 mb-4">
                            You don't have any pending appointment requests at the moment.
                        </p>
                    </div>
                </div>

                <!-- Requests list -->
                <div v-else class="requests-content">
                    <div class="mb-4 flex items-center gap-2 text-surface-600 dark:text-surface-400">
                        <i class="pi pi-info-circle"></i>
                        <span class="text-sm">
                            {{ appointmentRequests.length }} pending request{{ appointmentRequests.length !== 1 ? 's' : '' }}
                        </span>
                    </div>

                    <div class="request-list">
                        <Card 
                            v-for="appointment in appointmentRequests" 
                            :key="appointment.appId"
                            class="request-item"
                        >
                            <template #content>
                                <div class="request-content">
                                    <div class="patient-info">
                                        <div class="patient-avatar">
                                            <Avatar
                                                v-if="appointment.profile"
                                                :image="appointment.profile"
                                                shape="circle"
                                                size="large"
                                            />
                                            <Avatar
                                                v-else
                                                :label="appointment.name?.charAt(0) || 'P'"
                                                shape="circle"
                                                size="large"
                                                class="bg-blue-500 text-white"
                                            />
                                        </div>
                                        <div class="patient-details">
                                            <h4 class="patient-name">{{ appointment.name }}</h4>
                                            <p class="appointment-datetime">
                                                <i class="pi pi-calendar text-green-500"></i>
                                                <span>{{ appointment.date }} at {{ appointment.time }}</span>
                                            </p>
                                            <div v-if="appointment.reason" class="appointment-reason">
                                                <i class="pi pi-file-text text-surface-500 dark:text-surface-400"></i>
                                                <span class="text-surface-700 dark:text-surface-300">{{ appointment.reason }}</span>
                                            </div>
                                            <div class="request-metadata">
                                                <span class="text-xs text-surface-500 dark:text-surface-400">
                                                    Requested on {{ appointment.createdAt }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="request-actions">
                                        <div class="action-buttons">
                                            <Button 
                                                label="Details"
                                                icon="pi pi-info-circle" 
                                                size="small"
                                                outlined
                                                @click="displayAppointment(appointment)"
                                            />
                                            <Button 
                                                label="Accept"
                                                icon="pi pi-check" 
                                                size="small"
                                                severity="success"
                                                @click="selectedAppointment = appointment; confirmAcceptRequest($event)"
                                            />
                                            <Button 
                                                label="Reject"
                                                icon="pi pi-times" 
                                                size="small"
                                                severity="danger"
                                                outlined
                                                @click="selectedAppointment = appointment; confirmRejectRequest($event)"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </Card>
                    </div>
                </div>
            </template>
        </Card>

        <!-- Enhanced Appointment Details Dialog -->
        <Dialog 
            v-model:visible="visible" 
            modal 
            header="Appointment Request Details" 
            :style="{ width: '700px' }"
            class="appointment-details-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i class="pi pi-calendar-plus text-blue-500 mr-2"></i>
                    <span>Appointment Request Details</span>
                </div>
            </template>

            <div v-if="selectedAppointment" class="dialog-content">
                <!-- Patient Profile Section -->
                <div class="patient-profile-section">
                    <div class="flex items-center gap-4 mb-6">
                        <div class="profile-image">
                            <Avatar
                                v-if="selectedAppointment.profile"
                                :image="selectedAppointment.profile"
                                shape="circle"
                                size="xlarge"
                                class="border-2 border-surface-200 dark:border-surface-700"
                            />
                            <Avatar
                                v-else
                                :label="selectedAppointment.name?.charAt(0) || 'P'"
                                shape="circle"
                                size="xlarge"
                                class="bg-blue-500 text-white border-2 border-surface-200 dark:border-surface-700"
                            />
                        </div>
                        <div class="profile-info">
                            <h3 class="text-2xl font-semibold text-surface-900 dark:text-surface-0 mb-2">
                                {{ selectedAppointment.name }}
                            </h3>
                            <div class="contact-info space-y-2">
                                <div class="flex items-center gap-2 text-surface-600 dark:text-surface-400">
                                    <i class="pi pi-envelope"></i>
                                    <span>{{ selectedAppointment.email }}</span>
                                </div>
                                <div v-if="selectedAppointment.phone" class="flex items-center gap-2 text-surface-600 dark:text-surface-400">
                                    <i class="pi pi-phone"></i>
                                    <span>{{ selectedAppointment.phone }}</span>
                                </div>
                                <div v-if="selectedAppointment.address" class="flex items-center gap-2 text-surface-600 dark:text-surface-400">
                                    <i class="pi pi-map-marker"></i>
                                    <span>{{ selectedAppointment.address }}</span>
                                </div>
                                <div v-if="selectedAppointment.gender" class="flex items-center gap-2 text-surface-600 dark:text-surface-400">
                                    <i class="pi pi-user"></i>
                                    <span>{{ selectedAppointment.gender }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Appointment Details Section -->
                <div class="appointment-details-section">
                    <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-4">
                        Appointment Information
                    </h4>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div class="detail-item">
                            <label class="detail-label">Date</label>
                            <div class="detail-value">
                                <i class="pi pi-calendar text-green-500"></i>
                                <span>{{ selectedAppointment.date }}</span>
                            </div>
                        </div>
                        
                        <div class="detail-item">
                            <label class="detail-label">Time</label>
                            <div class="detail-value">
                                <i class="pi pi-clock text-orange-500"></i>
                                <span>{{ selectedAppointment.time }}</span>
                            </div>
                        </div>

                        <div class="detail-item">
                            <label class="detail-label">Request Date</label>
                            <div class="detail-value">
                                <i class="pi pi-calendar-plus text-blue-500"></i>
                                <span>{{ selectedAppointment.createdAt }}</span>
                            </div>
                        </div>

                        <div class="detail-item">
                            <label class="detail-label">Status</label>
                            <div class="detail-value">
                                <Tag value="Pending" severity="warning" />
                            </div>
                        </div>
                    </div>

                    <div v-if="selectedAppointment.reason" class="detail-item">
                        <label class="detail-label">Reason for Visit</label>
                        <div class="reason-content">
                            <p class="text-surface-900 dark:text-surface-0 bg-surface-50 dark:bg-surface-800 p-4 rounded-lg border">
                                {{ selectedAppointment.reason }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Additional Information -->
                <div class="additional-info">
                    <div class="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <p class="font-medium mb-1">Review Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Verify patient information before accepting</li>
                                <li>• Ensure the appointment time fits your schedule</li>
                                <li>• Consider the complexity of the stated reason</li>
                                <li>• Check for any scheduling conflicts</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-6">
                    <Button 
                        label="View Profile" 
                        icon="pi pi-user"
                        outlined
                        as="router-link"
                        :to="`/senior/${selectedAppointment?.sen_id}`"
                    />
                    <Button 
                        label="Reject" 
                        icon="pi pi-times"
                        severity="danger"
                        outlined
                        @click="confirmRejectRequest($event)"
                    />
                    <Button 
                        label="Accept" 
                        icon="pi pi-check"
                        severity="success"
                        @click="confirmAcceptRequest($event)"
                    />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
.appointment-requests-card {
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

.request-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.request-item {
    transition: all 0.2s ease;
    border: 1px solid var(--surface-border);
    border-left: 4px solid var(--orange-500);
}

.request-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.request-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    gap: 1rem;
}

.patient-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
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

.patient-details {
    flex: 1;
}

.patient-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 0.5rem 0;
}

.appointment-datetime {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text-color-secondary);
    margin-bottom: 0.25rem;
}

.appointment-reason {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 500;
}

.request-actions {
    flex-shrink: 0;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.dialog-header {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
}

.dialog-content {
    padding: 1rem 0;
}

.patient-profile-section {
    margin-bottom: 2rem;
}

.profile-info {
    flex: 1;
}

.contact-info {
    margin-top: 0.5rem;
}

.appointment-details-section {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--surface-border);
}

.detail-item {
    margin-bottom: 1rem;
}

.detail-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-color-secondary);
    margin-bottom: 0.5rem;
}

.detail-value {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-color);
}

.reason-content {
    margin-top: 0.5rem;
}

.additional-info {
    margin-top: 2rem;
}

.request-metadata {
    margin-top: 0.5rem;
}

/* Dark mode enhancements */
:global(.p-dark) .appointment-requests-card :deep(.p-card) {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

/* Responsive design */
@media (max-width: 768px) {
    .section-header {
        padding: 1rem 1rem 0;
    }
    
    .request-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .request-actions {
        width: 100%;
    }
    
    .action-buttons {
        width: 100%;
        justify-content: space-between;
    }
    
    .action-buttons button {
        flex: 1;
    }
    
    .dialog-content {
        padding: 0.5rem 0;
    }
    
    .patient-profile-section .flex {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }
    
    .contact-info {
        text-align: left;
    }
    
    .grid.grid-cols-1.md\\:grid-cols-2 {
        grid-template-columns: 1fr;
    }
}

/* Animation for new requests */
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

.request-item {
    animation: slideIn 0.3s ease;
}
</style>
