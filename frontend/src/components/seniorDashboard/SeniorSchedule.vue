<script setup>
import { seniorSchedules } from '@/service/SeniorScheduleSevice';
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const schedules = ref([]);
const visible = ref(false);
const submitting = ref(false);
const editVisible = ref(false);
const editingSchedule = ref(null);
const editingIndex = ref(-1);

const newSchedule = ref({
    label: '',
    date: '',
    time: ''
});

const editSchedule = ref({
    label: '',
    date: '',
    time: ''
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

const fetchSchedules = () => {
    seniorSchedules.getScheuldes().then((data) => (schedules.value = data));
};

const openScheduleDialog = () => {
    newSchedule.value = { label: '', date: '', time: '' };
    visible.value = true;
};

const cancelSchedule = () => {
    visible.value = false;
    newSchedule.value = { label: '', date: '', time: '' };
};

const addSchedule = async () => {
    if (newSchedule.value.label && newSchedule.value.date && newSchedule.value.time) {
        submitting.value = true;
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500));

            schedules.value.push({
                ...newSchedule.value,
                time: newSchedule.value.time.split(',').map((t) => t.trim())
            });

            toast.add({
                severity: 'success',
                summary: 'Schedule Added',
                detail: `${newSchedule.value.label} schedule has been created successfully!`,
                life: 3000
            });
            cancelSchedule();
        } catch (error) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Failed to add schedule. Please try again.',
                life: 3000
            });
        } finally {
            submitting.value = false;
        }
    } else {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields',
            life: 3000
        });
    }
};

const openEditDialog = (schedule, index) => {
    editingSchedule.value = { ...schedule };
    editingIndex.value = index;
    editSchedule.value = {
        label: schedule.label,
        date: schedule.date,
        time: Array.isArray(schedule.time) ? schedule.time.join(', ') : schedule.time
    };
    editVisible.value = true;
};

const cancelEdit = () => {
    editVisible.value = false;
    editingSchedule.value = null;
    editingIndex.value = -1;
    editSchedule.value = { label: '', date: '', time: '' };
};

const updateSchedule = async () => {
    if (editSchedule.value.label && editSchedule.value.date && editSchedule.value.time) {
        submitting.value = true;
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500));

            // Update the schedule in the array
            schedules.value[editingIndex.value] = {
                ...editSchedule.value,
                time: editSchedule.value.time.split(',').map((t) => t.trim())
            };

            toast.add({
                severity: 'success',
                summary: 'Schedule Updated',
                detail: `${editSchedule.value.label} schedule has been updated successfully!`,
                life: 3000
            });
            cancelEdit();
        } catch (error) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Failed to update schedule. Please try again.',
                life: 3000
            });
        } finally {
            submitting.value = false;
        }
    } else {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields',
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
    return newSchedule.value.label.trim() && newSchedule.value.date && newSchedule.value.time.trim();
};

const isEditFormValid = () => {
    return editSchedule.value.label.trim() && editSchedule.value.date && editSchedule.value.time.trim();
};

onMounted(() => {
    fetchSchedules();
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
                    <Column field="date" header="Frequency" style="min-width: 120px">
                        <template #body="{ data }">
                            <Tag
                                :value="data.date"
                                :severity="getFrequencyColor(data.date)"
                                class="text-sm"
                            />
                        </template>
                    </Column>
                    <Column field="time" header="Times" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="flex flex-wrap gap-1">
                                <Chip v-for="time in data.time" :key="time" :label="time" class="text-xs" />
                            </div>
                        </template>
                    </Column>
                    <Column header="Actions" style="width: 100px">
                        <template #body="{ data, index }">
                            <Button
                                icon="pi pi-pencil"
                                size="small"
                                outlined
                                v-tooltip.top="'Edit Schedule'"
                                @click="openEditDialog(data, index)"
                                class="w-full"
                            />
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
            </template>
        </Card>

        <!-- Enhanced Medicine Schedule Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            header="Add Medicine Schedule"
            :style="{ width: '500px' }"
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
                                v-model="newSchedule.date"
                                :options="frequencyOptions"
                                optionLabel="label"
                                optionValue="value"
                                class="w-full"
                            />
                            <label for="frequency">Frequency *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <InputText
                                id="timings"
                                v-model="newSchedule.time"
                                class="w-full"
                            />
                            <label for="timings">Times *</label>
                        </FloatLabel>
                        <small class="text-surface-500 dark:text-surface-400 mt-1 block">
                            Enter times separated by commas (e.g., 8:00 AM, 2:00 PM, 8:00 PM)
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
                                <li>• Use clear time formats (e.g., 8:00 AM, 6:30 PM)</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div v-if="newSchedule.label" class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-green-700 dark:text-green-300">
                        <i :class="getMedicineIcon(newSchedule.label)" class="text-green-500"></i>
                        <span class="text-sm font-medium">
                            Medicine: {{ newSchedule.label }}
                        </span>
                    </div>
                    <p v-if="newSchedule.date && newSchedule.time" class="text-xs text-green-600 dark:text-green-400 mt-1">
                        {{ newSchedule.date }} at {{ newSchedule.time }}
                    </p>
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
            :style="{ width: '500px' }"
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
                                v-model="editSchedule.date"
                                :options="frequencyOptions"
                                optionLabel="label"
                                optionValue="value"
                                class="w-full"
                            />
                            <label for="editFrequency">Frequency *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <InputText
                                id="editTimings"
                                v-model="editSchedule.time"
                                class="w-full"
                            />
                            <label for="editTimings">Times *</label>
                        </FloatLabel>
                        <small class="text-surface-500 dark:text-surface-400 mt-1 block">
                            Enter times separated by commas (e.g., 8:00 AM, 2:00 PM, 8:00 PM)
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
                            </ul>
                        </div>
                    </div>
                </div>

                <div v-if="editSchedule.label" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                        <i :class="getMedicineIcon(editSchedule.label)" class="text-blue-500"></i>
                        <span class="text-sm font-medium">
                            Updating: {{ editSchedule.label }}
                        </span>
                    </div>
                    <p v-if="editSchedule.date && editSchedule.time" class="text-xs text-blue-600 dark:text-blue-400 mt-1">
                        {{ editSchedule.date }} at {{ editSchedule.time }}
                    </p>
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
</style>
