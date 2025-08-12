<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useQuery, useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';

const toast = useToast();
const visible = ref(false);
const submitting = ref(false);
const editVisible = ref(false);
const editingSchedule = ref(null);
const editingIndex = ref(-1);

const newSchedule = ref({
    label: '',
    frequency: '',
    times: []  // Changed from string to array
});

const editSchedule = ref({
    label: '',
    frequency: '',
    times: []  // Changed from string to array
});

const frequencyOptions = [
    { label: 'Daily', value: 'Daily' },
    { label: 'Weekly', value: 'Weekly' },
    { label: 'Monday', value: 'Monday' },
    { label: 'Tuesday', value: 'Tuesday' },
    { label: 'Wednesday', value: 'Wednesday' },
    { label: 'Thursday', value: 'Thursday' },
    { label: 'Friday', value: 'Friday' },
    { label: 'Saturday', value: 'Saturday' },
    { label: 'Sunday', value: 'Sunday' },
    { label: 'As Needed', value: 'As Needed' }
];

// GraphQL queries and mutations
const GET_PRESCRIPTIONS = gql`
    query GetPrescriptionsForSenior {
        getPrescriptionsForSenior {
            presId
            senId
            docId
            medicationData
            time
            instructions
            createdAt
        }
    }
`;

const ADD_PRESCRIPTION = gql`
    mutation AddPrescription($medicationData: String!, $time: JSONString!, $instructions: String!) {
        addPrescription(
            medicationData: $medicationData
            time: $time
            instructions: $instructions
        ) {
            message
            status
        }
    }
`;

const UPDATE_PRESCRIPTION = gql`
    mutation UpdatePrescription($presId: Int!, $medicationData: String, $time: JSONString, $instructions: String) {
        updatePrescription(
            presId: $presId
            medicationData: $medicationData
            time: $time
            instructions: $instructions
        ) {
            message
            status
        }
    }
`;

const DELETE_PRESCRIPTION = gql`
    mutation DeletePrescription($presId: Int!) {
        deletePrescription(presId: $presId) {
            message
            status
        }
    }
`;

// Apollo composables
const { result, loading, error, refetch } = useQuery(GET_PRESCRIPTIONS);
const { mutate: addPrescription } = useMutation(ADD_PRESCRIPTION);
const { mutate: updatePrescription } = useMutation(UPDATE_PRESCRIPTION);
const { mutate: deletePrescription } = useMutation(DELETE_PRESCRIPTION);

// Computed property for schedules list
const schedules = computed(() => {
    const prescriptions = result.value?.getPrescriptionsForSenior || [];
    return prescriptions.map(prescription => {
        const timeData = typeof prescription.time === 'string'
            ? JSON.parse(prescription.time)
            : prescription.time;

        return {
            id: prescription.presId,
            label: prescription.medicationData,
            frequency: timeData?.frequency || 'Daily',
            times: timeData?.times || [],
            instructions: prescription.instructions
        };
    });
});

const openScheduleDialog = () => {
    newSchedule.value = { label: '', frequency: '', times: [new Date()] };  // Start with one time slot
    visible.value = true;
};

const cancelSchedule = () => {
    visible.value = false;
    newSchedule.value = { label: '', frequency: '', times: [] };
};

const addSchedule = async () => {
    if (!isFormValid()) {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields',
            life: 3000
        });
        return;
    }

    submitting.value = true;
    try {
        // Convert time Date objects to string format
        const timesArray = newSchedule.value.times.map(timeDate => formatTimeForBackend(timeDate));

        const timeData = {
            frequency: newSchedule.value.frequency,
            times: timesArray
        };

        const { data } = await addPrescription({
            medicationData: newSchedule.value.label.trim(),
            time: JSON.stringify(timeData),
            instructions: `Take as scheduled - ${newSchedule.value.frequency}`
        });

        const response = data?.addPrescription;

        if (response?.status === 201) {
            toast.add({
                severity: 'success',
                summary: 'Schedule Added',
                detail: response.message || `${newSchedule.value.label} schedule has been created successfully!`,
                life: 3000
            });

            // Refetch prescriptions to update the list
            await refetch();
            cancelSchedule();
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to add schedule. Please try again.',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error adding schedule:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to add schedule. Please try again.',
            life: 3000
        });
    } finally {
        submitting.value = false;
    }
};

const openEditDialog = (schedule, index) => {
    editingSchedule.value = { ...schedule };
    editingIndex.value = index;
    editSchedule.value = {
        label: schedule.label,
        frequency: schedule.frequency,
        times: schedule.times.map(time => {
            // Convert time string back to Date object for Calendar component
            const [hours, minutes] = time.split(':');
            const date = new Date();
            date.setHours(parseInt(hours), parseInt(minutes), 0, 0);
            return date;
        })
    };
    editVisible.value = true;
};

const cancelEdit = () => {
    editVisible.value = false;
    editingSchedule.value = null;
    editingIndex.value = -1;
    editSchedule.value = { label: '', frequency: '', times: [] };
};

const updateSchedule = async () => {
    if (!isEditFormValid()) {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields',
            life: 3000
        });
        return;
    }

    submitting.value = true;
    try {
        // Convert time Date objects to string format
        const timesArray = editSchedule.value.times.map(timeDate => formatTimeForBackend(timeDate));

        const timeData = {
            frequency: editSchedule.value.frequency,
            times: timesArray
        };

        const { data } = await updatePrescription({
            presId: editingSchedule.value.id,
            medicationData: editSchedule.value.label.trim(),
            time: JSON.stringify(timeData),
            instructions: `Take as scheduled - ${editSchedule.value.frequency}`
        });

        const response = data?.updatePrescription;

        if (response?.status === 200) {
            toast.add({
                severity: 'success',
                summary: 'Schedule Updated',
                detail: response.message || `${editSchedule.value.label} schedule has been updated successfully!`,
                life: 3000
            });

            // Refetch prescriptions to update the list
            await refetch();
            cancelEdit();
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to update schedule. Please try again.',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error updating schedule:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to update schedule. Please try again.',
            life: 3000
        });
    } finally {
        submitting.value = false;
    }
};

const deleteSchedule = async (schedule) => {
    try {
        const { data } = await deletePrescription({
            presId: schedule.id
        });

        const response = data?.deletePrescription;

        if (response?.status === 200) {
            toast.add({
                severity: 'success',
                summary: 'Schedule Deleted',
                detail: response.message || `${schedule.label} schedule has been deleted successfully!`,
                life: 3000
            });

            // Refetch prescriptions to update the list
            await refetch();
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to delete schedule. Please try again.',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error deleting schedule:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete schedule. Please try again.',
            life: 3000
        });
    }
};

const getMedicineIcon = (label) => {
    const lowerLabel = label.toLowerCase();
    if (lowerLabel.includes('vitamin') || lowerLabel.includes('supplement')) {
        return 'pi pi-heart';
    } else if (lowerLabel.includes('tablet') || lowerLabel.includes('pill')) {
        return 'pi pi-circle';
    } else if (lowerLabel.includes('injection')) {
        return 'pi pi-plus';
    } else if (lowerLabel.includes('syrup') || lowerLabel.includes('liquid')) {
        return 'pi pi-tint';
    }
    return 'pi pi-box';
};

const getFrequencyColor = (frequency) => {
    switch (frequency.toLowerCase()) {
        case 'daily':
            return 'success';
        case 'weekly':
            return 'info';
        case 'as needed':
            return 'warning';
        default:
            return 'secondary';
    }
};

const isFormValid = () => {
    return newSchedule.value.label.trim() &&
           newSchedule.value.frequency &&
           newSchedule.value.times.length > 0;
};

const isEditFormValid = () => {
    return editSchedule.value.label.trim() &&
           editSchedule.value.frequency &&
           editSchedule.value.times.length > 0;
};

// Add functions to manage time slots
const addTimeSlot = () => {
    newSchedule.value.times.push(new Date());
};

const removeTimeSlot = (index) => {
    if (newSchedule.value.times.length > 1) {
        newSchedule.value.times.splice(index, 1);
    }
};

const addEditTimeSlot = () => {
    editSchedule.value.times.push(new Date());
};

const removeEditTimeSlot = (index) => {
    if (editSchedule.value.times.length > 1) {
        editSchedule.value.times.splice(index, 1);
    }
};

// Helper function to format time for backend
const formatTimeForBackend = (timeDate) => {
    const hours = timeDate.getHours().toString().padStart(2, '0');
    const minutes = timeDate.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
};

onMounted(() => {
    // Data is automatically fetched by useQuery
});
</script>

<template>
    <Toast />
    <div class="medicine-schedule-card">
        <Card class="w-full">
            <template #header>
                <div class="section-header">
                    <i class="pi pi-calendar-clock text-blue-500"></i>
                    <h3 class="section-title">Medicine Schedules</h3>
                </div>
            </template>
            <template #content>
                <!-- Loading state -->
                <div v-if="loading" class="text-center py-8">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                    <p class="mt-4">Loading schedules...</p>
                </div>

                <!-- Error state -->
                <div v-else-if="error" class="text-center py-8">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                    <p class="text-red-600">Failed to load medicine schedules</p>
                    <Button label="Retry" @click="refetch" class="mt-3" />
                </div>

                <!-- Content -->
                <div v-else>
                    <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                        <p class="text-surface-600 dark:text-surface-400">
                            Keep track of your medication schedules to maintain your health routine.
                        </p>
                        <Button
                            label="Add Schedule"
                            icon="pi pi-plus"
                            severity="success"
                            outlined
                            @click="openScheduleDialog"
                            class="flex-shrink-0"
                        />
                    </div>

                    <DataTable
                        v-if="schedules && schedules.length"
                        :value="schedules"
                        :rows="5"
                        :paginator="schedules.length > 5"
                        responsiveLayout="scroll"
                        class="medicine-schedule-table"
                    >
                        <Column field="label" header="Medicine" style="min-width: 200px">
                            <template #body="{ data }">
                                <div class="flex items-center gap-2">
                                    <i :class="getMedicineIcon(data.label)" class="text-green-500"></i>
                                    <span class="font-medium text-surface-900 dark:text-surface-0">{{ data.label }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="frequency" header="Frequency" style="min-width: 120px">
                            <template #body="{ data }">
                                <Tag
                                    :value="data.frequency"
                                    :severity="getFrequencyColor(data.frequency)"
                                    class="text-sm"
                                />
                            </template>
                        </Column>
                        <Column field="times" header="Times" style="min-width: 200px">
                            <template #body="{ data }">
                                <div class="flex flex-wrap gap-1">
                                    <Chip v-for="time in data.times" :key="time" :label="time" class="text-xs" />
                                </div>
                            </template>
                        </Column>
                        <Column header="Actions" style="width: 120px">
                            <template #body="{ data, index }">
                                <div class="flex gap-1">
                                    <Button
                                        icon="pi pi-pencil"
                                        size="small"
                                        outlined
                                        v-tooltip.top="'Edit Schedule'"
                                        @click="openEditDialog(data, index)"
                                    />
                                    <Button
                                        icon="pi pi-trash"
                                        size="small"
                                        severity="danger"
                                        outlined
                                        v-tooltip.top="'Delete Schedule'"
                                        @click="deleteSchedule(data)"
                                    />
                                </div>
                            </template>
                        </Column>
                    </DataTable>

                    <div v-else class="empty-state">
                        <div class="text-center py-12">
                            <div class="text-surface-400 dark:text-surface-500 mb-4">
                                <i class="pi pi-calendar-clock text-6xl"></i>
                            </div>
                            <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                                No Medicine Schedules
                            </h4>
                            <p class="text-surface-500 dark:text-surface-400 mb-4">
                                Add your first medicine schedule to keep track of your medications.
                            </p>
                            <Button
                                label="Add Your First Schedule"
                                icon="pi pi-plus"
                                severity="success"
                                @click="openScheduleDialog"
                            />
                        </div>
                    </div>
                </div>
            </template>
        </Card>

        <!-- Add Medicine Schedule Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            header="Add Medicine Schedule"
            :style="{ width: '600px' }"
            :closable="!submitting"
            :dismissableMask="!submitting"
            class="medicine-schedule-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i class="pi pi-plus-circle text-green-500 mr-2"></i>
                    <span>Add Medicine Schedule</span>
                </div>
            </template>

            <div class="dialog-content">
                <div class="grid formgrid p-fluid">
                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <InputText
                                id="medicineLabel"
                                v-model="newSchedule.label"
                                class="w-full"
                            />
                            <label for="medicineLabel">Medicine Name *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <Select
                                id="frequency"
                                v-model="newSchedule.frequency"
                                :options="frequencyOptions"
                                optionLabel="label"
                                optionValue="value"
                                class="w-full"
                            />
                            <label for="frequency">Frequency *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-3">
                            Medicine Times *
                        </label>

                        <div class="space-y-3">
                            <div
                                v-for="(time, index) in newSchedule.times"
                                :key="index"
                                class="flex items-center gap-3"
                            >
                                <div class="flex-1">
                                    <Calendar
                                        v-model="newSchedule.times[index]"
                                        timeOnly
                                        hourFormat="24"
                                        showIcon
                                        :placeholder="`Time ${index + 1}`"
                                        class="w-full"
                                        inputClass="text-center"
                                    />
                                </div>
                                <Button
                                    v-if="newSchedule.times.length > 1"
                                    icon="pi pi-trash"
                                    size="small"
                                    severity="danger"
                                    outlined
                                    @click="removeTimeSlot(index)"
                                    v-tooltip.top="'Remove Time'"
                                />
                            </div>
                        </div>

                        <div class="mt-3">
                            <Button
                                label="Add Another Time"
                                icon="pi pi-plus"
                                size="small"
                                outlined
                                @click="addTimeSlot"
                                class="w-full"
                            />
                        </div>

                        <small class="text-surface-500 dark:text-surface-400 mt-2 block">
                            Use 24-hour format (e.g., 08:30 for 8:30 AM, 20:30 for 8:30 PM)
                        </small>
                    </div>
                </div>

                <div class="info-section">
                    <div class="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <p class="font-medium mb-1">Medicine Schedule Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Set consistent times for better medication adherence</li>
                                <li>• Include the full medicine name and dosage if needed</li>
                                <li>• Add multiple times per day as needed</li>
                                <li>• Reminders will be created automatically for each time</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div v-if="newSchedule.label" class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-green-700 dark:text-green-300 mb-2">
                        <i :class="getMedicineIcon(newSchedule.label)" class="text-green-500"></i>
                        <span class="text-sm font-medium">
                            Medicine: {{ newSchedule.label }}
                        </span>
                    </div>
                    <div v-if="newSchedule.frequency && newSchedule.times.length > 0" class="text-xs text-green-600 dark:text-green-400">
                        <p><strong>Frequency:</strong> {{ newSchedule.frequency }}</p>
                        <p><strong>Times:</strong>
                            {{ newSchedule.times.map(t => formatTimeForBackend(t)).join(', ') }}
                        </p>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-4">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        @click="cancelSchedule"
                        :disabled="submitting"
                        class="flex-shrink-0"
                    />
                    <Button
                        label="Add Schedule"
                        icon="pi pi-check"
                        severity="success"
                        @click="addSchedule"
                        :loading="submitting"
                        :disabled="!isFormValid()"
                        class="flex-shrink-0"
                    />
                </div>
            </template>
        </Dialog>

        <!-- Edit Medicine Schedule Dialog -->
        <Dialog
            v-model:visible="editVisible"
            modal
            header="Edit Medicine Schedule"
            :style="{ width: '600px' }"
            :closable="!submitting"
            :dismissableMask="!submitting"
            class="medicine-schedule-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i class="pi pi-pencil text-blue-500 mr-2"></i>
                    <span>Edit Medicine Schedule</span>
                </div>
            </template>

            <div class="dialog-content">
                <div class="grid formgrid p-fluid">
                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <InputText
                                id="editMedicineLabel"
                                v-model="editSchedule.label"
                                class="w-full"
                            />
                            <label for="editMedicineLabel">Medicine Name *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <Select
                                id="editFrequency"
                                v-model="editSchedule.frequency"
                                :options="frequencyOptions"
                                optionLabel="label"
                                optionValue="value"
                                class="w-full"
                            />
                            <label for="editFrequency">Frequency *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-3">
                            Medicine Times *
                        </label>

                        <div class="space-y-3">
                            <div
                                v-for="(time, index) in editSchedule.times"
                                :key="index"
                                class="flex items-center gap-3"
                            >
                                <div class="flex-1">
                                    <Calendar
                                        v-model="editSchedule.times[index]"
                                        timeOnly
                                        hourFormat="24"
                                        showIcon
                                        :placeholder="`Time ${index + 1}`"
                                        class="w-full"
                                        inputClass="text-center"
                                    />
                                </div>
                                <Button
                                    v-if="editSchedule.times.length > 1"
                                    icon="pi pi-trash"
                                    size="small"
                                    severity="danger"
                                    outlined
                                    @click="removeEditTimeSlot(index)"
                                    v-tooltip.top="'Remove Time'"
                                />
                            </div>
                        </div>

                        <div class="mt-3">
                            <Button
                                label="Add Another Time"
                                icon="pi pi-plus"
                                size="small"
                                outlined
                                @click="addEditTimeSlot"
                                class="w-full"
                            />
                        </div>

                        <small class="text-surface-500 dark:text-surface-400 mt-2 block">
                            Use 24-hour format (e.g., 08:30 for 8:30 AM, 20:30 for 8:30 PM)
                        </small>
                    </div>
                </div>

                <div class="info-section">
                    <div class="flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-amber-500 mt-1"></i>
                        <div class="text-sm text-amber-700 dark:text-amber-300">
                            <p class="font-medium mb-1">Editing Schedule Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Make sure to update times carefully to avoid missed doses</li>
                                <li>• Consider consulting your doctor before changing medication timing</li>
                                <li>• Keep track of any changes for medical records</li>
                                <li>• Existing reminders will be updated automatically</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div v-if="editSchedule.label" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-blue-700 dark:text-blue-300 mb-2">
                        <i :class="getMedicineIcon(editSchedule.label)" class="text-blue-500"></i>
                        <span class="text-sm font-medium">
                            Updating: {{ editSchedule.label }}
                        </span>
                    </div>
                    <div v-if="editSchedule.frequency && editSchedule.times.length > 0" class="text-xs text-blue-600 dark:text-blue-400">
                        <p><strong>Frequency:</strong> {{ editSchedule.frequency }}</p>
                        <p><strong>Times:</strong>
                            {{ editSchedule.times.map(t => formatTimeForBackend(t)).join(', ') }}
                        </p>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-4">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        @click="cancelEdit"
                        :disabled="submitting"
                        class="flex-shrink-0"
                    />
                    <Button
                        label="Update Schedule"
                        icon="pi pi-check"
                        severity="info"
                        @click="updateSchedule"
                        :loading="submitting"
                        :disabled="!isEditFormValid()"
                        class="flex-shrink-0"
                    />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
.medicine-schedule-card {
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

.medicine-schedule-table {
    border-radius: 8px;
    overflow: hidden;
}

.empty-state {
    background: var(--surface-ground);
    border-radius: 12px;
    border: 2px dashed var(--surface-border);
}

.dialog-header {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
}

.dialog-content {
    padding: 1.5rem 0;
}

.info-section {
    margin-top: 2rem;
}

/* Enhanced spacing for form fields */
.field.mb-4 {
    margin-bottom: 1.5rem !important;
}

/* Dark mode enhancements */
:global(.p-dark) .medicine-schedule-card :deep(.p-card) {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

:global(.p-dark) .dialog-header {
    color: var(--text-color);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .section-header {
        padding: 1rem 1rem 0;
    }

    .field.mb-4 {
        margin-bottom: 1.25rem !important;
    }

    .dialog-content {
        padding: 1rem 0;
    }
}

/* Animation enhancements */
.medicine-schedule-table :deep(tr) {
    transition: all 0.3s ease;
}

.medicine-schedule-table :deep(tr:hover) {
    background: var(--surface-hover);
}

:deep(.p-button) {
    transition: all 0.3s ease;
}

:deep(.p-button:hover) {
    transform: translateY(-1px);
}

/* Chip styling for times */
:deep(.p-chip) {
    background: var(--primary-100);
    color: var(--primary-800);
}

:global(.p-dark) :deep(.p-chip) {
    background: var(--primary-900);
    color: var(--primary-100);
}

/* Time picker enhancements */
:deep(.p-calendar) {
    width: 100%;
}

:deep(.p-calendar .p-inputtext) {
    text-align: center;
    font-family: monospace;
    font-size: 1.1rem;
    font-weight: 500;
}

.time-slot-container {
    background: var(--surface-100);
    border-radius: 8px;
    padding: 0.75rem;
    border: 1px solid var(--surface-border);
}

:global(.p-dark) .time-slot-container {
    background: var(--surface-800);
}

/* Add time button styling */
:deep(.p-button-outlined) {
    border-style: dashed;
}

:deep(.p-button-outlined):hover {
    background: var(--surface-100);
}

:global(.p-dark) :deep(.p-button-outlined):hover {
    background: var(--surface-800);
}
</style>
