<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { vitals as vitalService } from '@/service/VitalService';

const toast = useToast();
const props = defineProps({
    ez_id: String,
});

const vitals = ref([]);
const vitalTypes = ref([]);
const visible = ref(false);
const submitting = ref(false);

const vitalForm = ref({
    selectedType: null,
    reading: ''
});

onMounted(() => {
    vitalService.getVitalsBySenior(props.ez_id).then((data) => {
        // Sort by most recent first
        vitals.value = data.sort((a, b) => {
            const dateA = new Date(`${a.date} ${a.time}`);
            const dateB = new Date(`${b.date} ${b.time}`);
            return dateB - dateA;
        });
    });
    vitalTypes.value = vitalService.getVitalTypes();
});

const selectedVitalType = computed(() => {
    return vitalTypes.value.find(type => type.value === vitalForm.value.selectedType?.value);
});

const openVitalDialog = () => {
    vitalForm.value = { selectedType: null, reading: '' };
    visible.value = true;
};

const cancelVital = () => {
    visible.value = false;
    vitalForm.value = { selectedType: null, reading: '' };
};

const submitVital = async () => {
    if (vitalForm.value.selectedType && vitalForm.value.reading) {
        const vitalData = {
            sen_id: props.ez_id,
            label: vitalForm.value.selectedType.label,
            value: vitalForm.value.selectedType.value,
            unit: vitalForm.value.selectedType.unit,
            reading: vitalForm.value.reading
        };

        submitting.value = true;
        try {
            const newVital = await vitalService.addVital(vitalData);
            // Add to beginning of array to maintain descending order
            vitals.value.unshift(newVital);
            toast.add({
                severity: 'success',
                summary: 'Vital Logged',
                detail: `${vitalForm.value.selectedType.label} reading recorded successfully`,
                life: 3000
            });
            cancelVital();
        } catch (error) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Failed to log vital. Please try again.',
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

const getVitalIcon = (vitalType) => {
    switch (vitalType.toLowerCase()) {
        case 'blood pressure':
            return 'pi pi-heart';
        case 'heart rate':
            return 'pi pi-heart-fill';
        case 'temperature':
            return 'pi pi-sun';
        case 'blood sugar':
            return 'pi pi-chart-line';
        case 'weight':
            return 'pi pi-chart-bar';
        case 'oxygen saturation':
            return 'pi pi-circle';
        default:
            return 'pi pi-heart';
    }
};

const isFormValid = () => {
    return vitalForm.value.selectedType && vitalForm.value.reading.trim();
};
</script>

<template>
    <Toast />
    <div class="vital-logs-card">
        <Card class="w-full">
            <template #header>
                <div class="section-header">
                    <i class="pi pi-heart text-red-500"></i>
                    <h3 class="section-title">Vital Logs</h3>
                </div>
            </template>
            <template #content>
                <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                    <p class="text-surface-600 dark:text-surface-400">
                        Track and monitor your vital signs over time to maintain good health.
                    </p>
                    <Button
                        label="Log New Vital"
                        icon="pi pi-plus"
                        severity="success"
                        outlined
                        @click="openVitalDialog"
                        class="flex-shrink-0"
                    />
                </div>

                <DataTable
                    v-if="vitals && vitals.length"
                    :value="vitals"
                    :rows="8"
                    :paginator="vitals.length > 8"
                    responsiveLayout="scroll"
                    class="vital-logs-table"
                >
                    <Column field="label" header="Vital Type" style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <i :class="getVitalIcon(data.label)" class="text-blue-500"></i>
                                <span class="font-medium text-surface-900 dark:text-surface-0">{{ data.label }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="reading" header="Reading" style="min-width: 120px">
                        <template #body="{ data }">
                            <div class="text-lg font-semibold text-surface-800 dark:text-surface-200">
                                {{ data.reading }}
                                <span class="text-sm font-normal text-surface-500 dark:text-surface-400">{{ data.unit }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="date" header="Date" style="min-width: 100px" sortable>
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <i class="pi pi-calendar text-green-500"></i>
                                <span class="text-surface-700 dark:text-surface-300">{{ data.date }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="time" header="Time" style="min-width: 80px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <i class="pi pi-clock text-orange-500"></i>
                                <span class="text-surface-700 dark:text-surface-300">{{ data.time }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column header="Status" style="min-width: 100px">
                        <template #body="{ data }">
                            <Tag
                                v-if="data.statusInfo?.status !== 'irrelevant'"
                                :value="data.statusInfo?.status"
                                :severity="data.statusInfo?.status === 'Normal' ? 'success' :
                                          data.statusInfo?.status === 'High' ? 'danger' :
                                          data.statusInfo?.status === 'Low' ? 'warning' : 'secondary'"
                                class="text-sm"
                            />
                            <span v-else class="text-surface-400 dark:text-surface-500">
                                -
                            </span>
                        </template>
                    </Column>
                </DataTable>

                <div v-else class="empty-state">
                    <div class="text-center py-12">
                        <div class="text-surface-400 dark:text-surface-500 mb-4">
                            <i class="pi pi-heart text-6xl"></i>
                        </div>
                        <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                            No Vital Logs Found
                        </h4>
                        <p class="text-surface-500 dark:text-surface-400 mb-4">
                            Start tracking your health by logging your first vital signs.
                        </p>
                        <Button
                            label="Log Your First Vital"
                            icon="pi pi-plus"
                            severity="success"
                            @click="openVitalDialog"
                        />
                    </div>
                </div>
            </template>
        </Card>

        <!-- Enhanced Vital Log Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            header="Log Vital Signs"
            :style="{ width: '500px' }"
            :closable="!submitting"
            :dismissableMask="!submitting"
            class="vital-log-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i class="pi pi-heart-fill text-red-500 mr-2"></i>
                    <span>Log Vital Signs</span>
                </div>
            </template>

            <div class="dialog-content">
                <div class="grid formgrid p-fluid">
                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <Select
                                id="vitalType"
                                v-model="vitalForm.selectedType"
                                :options="vitalTypes"
                                optionLabel="label"
                                class="w-full"
                            />
                            <label for="vitalType">Select Vital Type *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <InputText
                                id="reading"
                                v-model="vitalForm.reading"
                                class="w-full"
                                :placeholder="selectedVitalType?.placeholder || 'Enter reading'"
                            />
                            <label for="reading">
                                Reading *
                                <span v-if="selectedVitalType" class="text-surface-500 dark:text-surface-400">
                                    ({{ selectedVitalType.unit }})
                                </span>
                            </label>
                        </FloatLabel>
                    </div>
                </div>

                <div class="info-section">
                    <div class="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <p class="font-medium mb-1">Vital Logging Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Record vitals at consistent times for accurate tracking</li>
                                <li>• Ensure your measuring devices are properly calibrated</li>
                                <li>• Date and time will be automatically recorded</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div v-if="selectedVitalType" class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-green-700 dark:text-green-300">
                        <i :class="getVitalIcon(selectedVitalType.label)" class="text-green-500"></i>
                        <span class="text-sm font-medium">
                            Selected: {{ selectedVitalType.label }}
                        </span>
                    </div>
                    <p class="text-xs text-green-600 dark:text-green-400 mt-1">
                        {{ selectedVitalType.placeholder }}
                    </p>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-4">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        @click="cancelVital"
                        :disabled="submitting"
                        class="flex-shrink-0"
                    />
                    <Button
                        label="Log Vital"
                        icon="pi pi-check"
                        severity="success"
                        @click="submitVital"
                        :loading="submitting"
                        :disabled="!isFormValid()"
                        class="flex-shrink-0"
                    />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
.vital-logs-card {
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

.vital-logs-table {
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
:global(.p-dark) .vital-logs-card :deep(.p-card) {
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
.vital-logs-table :deep(tr) {
    transition: all 0.3s ease;
}

.vital-logs-table :deep(tr:hover) {
    background: var(--surface-hover);
}

:deep(.p-button) {
    transition: all 0.3s ease;
}

:deep(.p-button:hover) {
    transform: translateY(-1px);
}

/* Status color overrides for better visibility */
:deep(.p-tag.p-tag-success) {
    background: var(--green-100);
    color: var(--green-800);
}

:deep(.p-tag.p-tag-danger) {
    background: var(--red-100);
    color: var(--red-800);
}

:deep(.p-tag.p-tag-warning) {
    background: var(--yellow-100);
    color: var(--yellow-800);
}

:global(.p-dark) :deep(.p-tag.p-tag-success) {
    background: var(--green-900);
    color: var(--green-100);
}

:global(.p-dark) :deep(.p-tag.p-tag-danger) {
    background: var(--red-900);
    color: var(--red-100);
}

:global(.p-dark) :deep(.p-tag.p-tag-warning) {
    background: var(--yellow-900);
    color: var(--yellow-100);
}
</style>
