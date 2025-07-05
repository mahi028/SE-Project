<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { vitals as vitalService } from '@/service/VitalService';
import Chart from 'primevue/chart';

const props = defineProps({
    ez_id: {
        type: String,
        required: true
    }
});

const vitals = ref([]);
const selectedVitalType = ref('blood_pressure');
const loading = ref(false);
const chartData = ref({});
const chartOptions = ref({});

const vitalTypes = computed(() => {
    return vitalService.getVitalTypes().map(type => ({
        label: type.label,
        value: type.value
    }));
});

const filteredVitals = computed(() => {
    return vitals.value
        .filter(vital => vital.value === selectedVitalType.value)
        .sort((a, b) => new Date(a.loggedAt) - new Date(b.loggedAt));
});

const processChartData = () => {
    const filtered = filteredVitals.value;

    if (filtered.length === 0) {
        chartData.value = {
            labels: [],
            datasets: []
        };
        return;
    }

    const labels = filtered.map(vital => {
        const date = new Date(vital.loggedAt);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    });

    let datasets = [];

    if (selectedVitalType.value === 'blood_pressure') {
        // Special handling for blood pressure (systolic/diastolic)
        const systolicData = [];
        const diastolicData = [];

        filtered.forEach(vital => {
            const match = vital.reading.match(/(\d+)\/(\d+)/);
            if (match) {
                systolicData.push(parseInt(match[1]));
                diastolicData.push(parseInt(match[2]));
            }
        });

        datasets = [
            {
                label: 'Systolic',
                data: systolicData,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: false
            },
            {
                label: 'Diastolic',
                data: diastolicData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: false
            }
        ];
    } else {
        // Regular vitals
        const data = filtered.map(vital => parseFloat(vital.reading));
        const vitalType = vitalService.getVitalTypes().find(t => t.value === selectedVitalType.value);

        datasets = [{
            label: vitalType?.label || 'Value',
            data: data,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true
        }];
    }

    chartData.value = {
        labels: labels,
        datasets: datasets
    };
};

const setupChartOptions = () => {
    const vitalType = vitalService.getVitalTypes().find(t => t.value === selectedVitalType.value);

    chartOptions.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: `${vitalType?.label || 'Vital'} Trend`,
                font: {
                    size: 16,
                    weight: 'bold'
                }
            },
            legend: {
                display: true,
                position: 'top'
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(context) {
                        const unit = vitalType?.unit || '';
                        return `${context.dataset.label}: ${context.parsed.y} ${unit}`;
                    }
                }
            }
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Date & Time'
                },
                grid: {
                    display: false
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: `Value (${vitalType?.unit || ''})`
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                },
                beginAtZero: false
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };
};

const fetchVitals = async () => {
    loading.value = true;
    try {
        const data = await vitalService.getVitalsBySenior(props.ez_id);
        vitals.value = data;
        processChartData();
        setupChartOptions();
    } catch (error) {
        console.error('Failed to fetch vitals:', error);
    } finally {
        loading.value = false;
    }
};

const onVitalTypeChange = () => {
    processChartData();
    setupChartOptions();
};

watch(selectedVitalType, onVitalTypeChange);

onMounted(() => {
    fetchVitals();
});
</script>

<template>
    <div class="card">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
            <h3 class="text-2xl font-semibold">Vital Trends</h3>
            <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
                <label for="vitalTypeSelect" class="text-base font-medium text-gray-700">
                    Select Vital:
                </label>
                <Dropdown
                    id="vitalTypeSelect"
                    v-model="selectedVitalType"
                    :options="vitalTypes"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select vital type"
                    class="w-48"
                />
                <Button
                    icon="pi pi-refresh"
                    @click="fetchVitals"
                    rounded
                    outlined
                    size="small"
                    v-tooltip.top="'Refresh data'"
                />
            </div>
        </div>

        <div v-if="loading" class="text-center py-8">
            <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
            <p class="text-gray-600 mt-3">Loading vital trends...</p>
        </div>

        <div v-else-if="filteredVitals.length === 0" class="text-center py-12">
            <div class="text-gray-500 mb-3">
                <i class="pi pi-chart-line text-5xl"></i>
            </div>
            <p class="text-gray-600 text-lg">
                No data available for {{ vitalTypes.find(t => t.value === selectedVitalType)?.label || 'selected vital' }}
            </p>
            <p class="text-gray-500 text-sm mt-2">
                Start logging vitals to see trends here
            </p>
        </div>

        <div v-else class="chart-container">
            <Chart
                type="line"
                :data="chartData"
                :options="chartOptions"
                class="chart"
            />

            <!-- Summary Statistics -->
            <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <div class="text-sm text-blue-600 font-medium">Total Readings</div>
                    <div class="text-2xl font-bold text-blue-800">{{ filteredVitals.length }}</div>
                </div>

                <div class="bg-green-50 p-4 rounded-lg" v-if="selectedVitalType !== 'blood_pressure'">
                    <div class="text-sm text-green-600 font-medium">Latest Reading</div>
                    <div class="text-2xl font-bold text-green-800">
                        {{ filteredVitals[filteredVitals.length - 1]?.reading }}
                        {{ vitalTypes.find(t => t.value === selectedVitalType)?.unit || '' }}
                    </div>
                </div>

                <div class="bg-green-50 p-4 rounded-lg" v-else>
                    <div class="text-sm text-green-600 font-medium">Latest BP</div>
                    <div class="text-2xl font-bold text-green-800">
                        {{ filteredVitals[filteredVitals.length - 1]?.reading }} mmHg
                    </div>
                </div>

                <div class="bg-purple-50 p-4 rounded-lg">
                    <div class="text-sm text-purple-600 font-medium">Date Range</div>
                    <div class="text-sm font-bold text-purple-800">
                        {{ filteredVitals.length > 0 ?
                            `${new Date(filteredVitals[0].loggedAt).toLocaleDateString()} -
                             ${new Date(filteredVitals[filteredVitals.length - 1].loggedAt).toLocaleDateString()}`
                            : 'N/A'
                        }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.chart-container {
    width: 100%;
}

.chart {
    height: 400px;
    width: 100%;
}

@media (max-width: 768px) {
    .chart {
        height: 300px;
    }
}
</style>
