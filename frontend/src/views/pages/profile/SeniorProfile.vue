<script setup>
import { ref, onMounted } from 'vue'
import { seniorService } from '@/service/SeniorService'
import { appointmentService } from '@/service/AppointmentService'
import { vitals as vitalService } from '@/service/VitalService'
import { useLoginStore } from '@/store/loginStore'
import { useRoute } from 'vue-router'
import InfoItem from '@/components/InfoItem.vue'
import VitalLogs from '@/components/seniorDashboard/VitalLogs.vue'
import VitalTrend from '@/components/VitalTrend.vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const loginStore = useLoginStore()
const userDetails = ref({})
const appointments = ref([])
const vitals = ref([])
const loading = ref(false)

const toast = useToast()
const confirm = useConfirm()

// Add method to get vital icons for doctor view
const getVitalIcon = (vitalType) => {
  switch (vitalType.toLowerCase()) {
    case 'blood pressure':
      return 'pi pi-heart'
    case 'heart rate':
      return 'pi pi-heart-fill'
    case 'temperature':
      return 'pi pi-sun'
    case 'blood sugar':
      return 'pi pi-chart-line'
    case 'weight':
      return 'pi pi-chart-bar'
    case 'oxygen saturation':
      return 'pi pi-circle'
    default:
      return 'pi pi-heart'
  }
}

onMounted(async () => {
  loading.value = true
  try {
    userDetails.value = await seniorService.getSenior({ "ez_id": route.params.ez_id })

    // Only show appointments and vitals if a doctor is viewing the senior's profile
    if (loginStore.role === 'doctor') {
      // Doctor viewing senior profile - show appointments between them
      appointments.value = await appointmentService.getAppointmentsBetweenDoctorAndSenior(
        loginStore.ez_id,
        route.params.ez_id
      )
      // Also load vitals for doctor to review
      vitals.value = await vitalService.getVitalsBySenior(route.params.ez_id)
    }
  } catch (error) {
    console.error('Failed to load user data:', error)
  } finally {
    loading.value = false
  }
})

const cancelAppointment = (appointment) => {
  confirm.require({
    message: `Are you sure you want to cancel the appointment with ${userDetails.value.name} on ${appointment.date} at ${appointment.time}?`,
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
        await new Promise(resolve => setTimeout(resolve, 500))

        // Remove appointment from list
        appointments.value = appointments.value.filter(apt =>
          !(apt.sen_id === appointment.sen_id && apt.date === appointment.date && apt.time === appointment.time)
        )

        toast.add({
          severity: 'success',
          summary: 'Appointment Cancelled',
          detail: 'The appointment has been cancelled successfully.',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to cancel appointment. Please try again.',
          life: 3000
        })
      }
    }
  })
}

const isUpcomingAppointment = (appointment) => {
  const appointmentDateTime = new Date(`${appointment.date} ${appointment.time}`)
  return appointmentDateTime >= new Date()
}

const showMedicalHistoryDialog = ref(false)
const showPrescriptionDialog = ref(false)
const medicalHistory = ref([])
const prescriptions = ref([])
const loadingMedicalHistory = ref(false)
const loadingPrescriptions = ref(false)

const viewMedicalHistory = async () => {
  loadingMedicalHistory.value = true
  try {
    // Simulate API call to fetch medical history
    await new Promise(resolve => setTimeout(resolve, 500))

    // Mock medical history data
    medicalHistory.value = [
      {
        id: 'MH001',
        date: '2024-01-15',
        condition: 'Hypertension',
        diagnosis: 'Essential Hypertension',
        treatment: 'Prescribed Amlodipine 5mg daily',
        doctor: 'Dr. Rajesh Kumar',
        notes: 'Blood pressure well controlled with medication'
      },
      {
        id: 'MH002',
        date: '2023-12-10',
        condition: 'Diabetes Type 2',
        diagnosis: 'Type 2 Diabetes Mellitus',
        treatment: 'Metformin 500mg twice daily',
        doctor: 'Dr. Priya Sharma',
        notes: 'HbA1c levels improving, continue current medication'
      },
      {
        id: 'MH003',
        date: '2023-11-05',
        condition: 'Arthritis',
        diagnosis: 'Osteoarthritis of knee joints',
        treatment: 'Physiotherapy and pain management',
        doctor: 'Dr. Vikram Malhotra',
        notes: 'Patient responding well to physiotherapy'
      }
    ]

    showMedicalHistoryDialog.value = true
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load medical history. Please try again.',
      life: 3000
    })
  } finally {
    loadingMedicalHistory.value = false
  }
}

const viewPrescriptions = async () => {
  loadingPrescriptions.value = true
  try {
    // Simulate API call to fetch prescriptions
    await new Promise(resolve => setTimeout(resolve, 500))

    // Mock prescription data
    prescriptions.value = [
      {
        id: 'RX001',
        date: '2024-01-15',
        doctor: 'Dr. Rajesh Kumar',
        medications: [
          {
            name: 'Amlodipine',
            strength: '5mg',
            frequency: 'Once daily',
            duration: '30 days',
            instructions: 'Take with food in the morning'
          },
          {
            name: 'Aspirin',
            strength: '75mg',
            frequency: 'Once daily',
            duration: '30 days',
            instructions: 'Take after dinner'
          }
        ],
        notes: 'Continue current regimen, follow up in 4 weeks'
      },
      {
        id: 'RX002',
        date: '2023-12-10',
        doctor: 'Dr. Priya Sharma',
        medications: [
          {
            name: 'Metformin',
            strength: '500mg',
            frequency: 'Twice daily',
            duration: '30 days',
            instructions: 'Take with meals'
          },
          {
            name: 'Glimepiride',
            strength: '2mg',
            frequency: 'Once daily',
            duration: '30 days',
            instructions: 'Take before breakfast'
          }
        ],
        notes: 'Monitor blood glucose levels regularly'
      }
    ]

    showPrescriptionDialog.value = true
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load prescriptions. Please try again.',
      life: 3000
    })
  } finally {
    loadingPrescriptions.value = false
  }
}
</script>

<template>
  <Toast />
  <ConfirmDialog />
  <div class="p-4 max-w-7xl mx-auto">
    <Card class="w-full">
      <template #content>
        <!-- Profile Header -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center mb-5">
          <!-- Profile Image -->
          <div class="flex justify-center">
						<img
						src="/images/user.png"
						alt="Profile Picture"
						class="w-64 h-64 object-cover rounded-xl shadow"
						/>
					</div>

          <!-- Basic Details -->
          <div class="md:col-span-2">
            <h2 class="text-3xl font-bold mb-4">{{ userDetails.name }}</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <InfoItem type="basic" label="Address" :value="userDetails.address + ', ' + userDetails.pincode" />
              <InfoItem type="basic" label="Contact" :value="userDetails.phone" />
              <InfoItem
                type="basic"
                label="Email"
                :value="userDetails.email"
              />
            </div>
          </div>
        </div>
        <Divider />

        <!-- Doctor Action Buttons - Only for doctors -->
        <div v-if="loginStore.role === 'doctor'" class="mb-8">
          <h3 class="text-2xl font-semibold mb-4 flex items-center gap-2">
            <i class="pi pi-user-md text-blue-500"></i>
            Medical Information
          </h3>
          <div class="flex flex-wrap gap-3">
            <Button
              label="View Medical History"
              icon="pi pi-file-text"
              severity="info"
              @click="viewMedicalHistory"
              :loading="loadingMedicalHistory"
              class="flex-shrink-0"
            />
            <Button
              label="View Prescriptions"
              icon="pi pi-receipt"
              severity="success"
              @click="viewPrescriptions"
              :loading="loadingPrescriptions"
              class="flex-shrink-0"
            />
          </div>
          <Divider />
        </div>

        <!-- Appointment History Section - Only for doctors -->
        <div class="mt-8" v-if="loginStore.role === 'doctor'">
          <h3 class="text-2xl font-semibold mb-6">Appointment History with {{ userDetails.name }}</h3>
          <div v-if="loading" class="text-center py-6">
            <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
          </div>
          <div v-else-if="appointments.length === 0" class="text-center py-10">
            <div class="text-gray-500 mb-3">
              <i class="pi pi-calendar-times text-5xl"></i>
            </div>
            <p class="text-gray-600 text-lg">No appointments found between you and this patient.</p>
          </div>
          <div v-else>
            <DataTable
              :value="appointments"
              :rows="10"
              :paginator="appointments.length > 10"
              responsiveLayout="scroll"
              class="p-datatable-lg text-base"
            >
              <Column field="date" header="Date" sortable style="width: 20%">
                <template #body="{ data }">
                  <span class="font-semibold text-base">{{ data.date }}</span>
                </template>
              </Column>
              <Column field="time" header="Time" style="width: 15%">
                <template #body="{ data }">
                  <span class="text-base">{{ data.time }}</span>
                </template>
              </Column>
              <Column field="reason" header="Reason" style="width: 50%">
                <template #body="{ data }">
                  <span class="text-base">{{ data.reason }}</span>
                </template>
              </Column>
              <Column header="Actions" style="width: 15%">
                <template #body="{ data }">
                  <Button
                    v-if="isUpcomingAppointment(data)"
                    icon="pi pi-times"
                    size="small"
                    severity="danger"
                    outlined
                    @click="cancelAppointment(data)"
                    v-tooltip.top="'Cancel Appointment'"
                  />
                  <span v-else class="text-surface-500 text-sm">Completed</span>
                </template>
              </Column>
            </DataTable>
          </div>
        </div>

        <Divider v-if="loginStore.role === 'doctor'" />

        <!-- Vital Logs and Trends Section - Only for doctors -->
        <div v-if="loginStore.role === 'doctor'" class="mt-8 space-y-8">
          <!-- Vital Trends Chart -->
          <div>
            <h3 class="text-2xl font-semibold mb-6 flex items-center gap-2">
              <i class="pi pi-chart-line text-blue-500"></i>
              <span>{{ userDetails.name }}'s Vital Trends</span>
            </h3>
            <VitalTrend :ez_id="route.params.ez_id" />
          </div>

          <!-- Vital Logs Table -->
          <div>
            <h3 class="text-2xl font-semibold mb-6 flex items-center gap-2">
              <i class="pi pi-heart text-red-500"></i>
              <span>{{ userDetails.name }}'s Vital Logs</span>
            </h3>

            <div v-if="loading" class="text-center py-6">
              <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
            </div>
            <div v-else-if="vitals.length === 0" class="text-center py-10">
              <div class="text-gray-500 mb-3">
                <i class="pi pi-heart text-5xl"></i>
              </div>
              <p class="text-gray-600 text-lg">No vital logs found for this patient.</p>
            </div>
            <div v-else>
              <DataTable
                :value="vitals"
                :rows="10"
                :paginator="vitals.length > 10"
                responsiveLayout="scroll"
                class="p-datatable-lg text-base"
                sortField="date"
                :sortOrder="-1"
              >
                <Column field="label" header="Vital Type" style="width: 25%">
                  <template #body="{ data }">
                    <div class="flex items-center gap-2">
                      <i :class="getVitalIcon(data.label)" class="text-blue-500"></i>
                      <span class="text-base font-medium">{{ data.label }}</span>
                    </div>
                  </template>
                </Column>
                <Column field="reading" header="Reading" style="width: 20%">
                  <template #body="{ data }">
                    <span class="font-semibold text-base">{{ data.reading }} {{ data.unit }}</span>
                  </template>
                </Column>
                <Column field="date" header="Date" sortable style="width: 20%">
                  <template #body="{ data }">
                    <span class="text-base">{{ data.date }}</span>
                  </template>
                </Column>
                <Column field="time" header="Time" style="width: 20%">
                  <template #body="{ data }">
                    <span class="text-base">{{ data.time }}</span>
                  </template>
                </Column>
                <Column header="Status" style="width: 15%">
                  <template #body="{ data }">
                    <span
                      v-if="data.statusInfo?.status === 'irrelevant'"
                      class="text-gray-500 font-semibold text-base"
                    >
                      -
                    </span>
                    <Tag
                      v-else
                      :value="data.statusInfo?.status"
                      :severity="data.statusInfo?.status === 'Normal' ? 'success' :
                                data.statusInfo?.status === 'High' ? 'danger' :
                                data.statusInfo?.status === 'Low' ? 'warning' : 'secondary'"
                      class="text-sm"
                    />
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Medical History Dialog -->
    <Dialog
      v-model:visible="showMedicalHistoryDialog"
      modal
      header="Medical History"
      :style="{ width: '800px' }"
      class="medical-history-dialog"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-file-text text-blue-500"></i>
          <span class="text-xl font-semibold">{{ userDetails.name }}'s Medical History</span>
        </div>
      </template>

      <div class="space-y-4">
        <div v-if="medicalHistory.length === 0" class="text-center py-8">
          <i class="pi pi-file text-4xl text-surface-400 mb-3"></i>
          <p class="text-surface-500 dark:text-surface-400">No medical history records found.</p>
        </div>

        <Card
          v-for="record in medicalHistory"
          :key="record.id"
          class="medical-record-card"
        >
          <template #content>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Date</label>
                  <p class="text-surface-900 dark:text-surface-0 font-semibold">{{ record.date }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Condition</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.condition }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Diagnosis</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.diagnosis }}</p>
                </div>
              </div>
              <div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Treating Doctor</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.doctor }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Treatment</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.treatment }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Notes</label>
                  <p class="text-surface-700 dark:text-surface-300 text-sm">{{ record.notes }}</p>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <Button
            label="Close"
            icon="pi pi-times"
            outlined
            @click="showMedicalHistoryDialog = false"
          />
        </div>
      </template>
    </Dialog>

    <!-- Prescriptions Dialog -->
    <Dialog
      v-model:visible="showPrescriptionDialog"
      modal
      header="Prescriptions"
      :style="{ width: '900px' }"
      class="prescription-dialog"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-receipt text-green-500"></i>
          <span class="text-xl font-semibold">{{ userDetails.name }}'s Prescriptions</span>
        </div>
      </template>

      <div class="space-y-6">
        <div v-if="prescriptions.length === 0" class="text-center py-8">
          <i class="pi pi-receipt text-4xl text-surface-400 mb-3"></i>
          <p class="text-surface-500 dark:text-surface-400">No prescription records found.</p>
        </div>

        <Card
          v-for="prescription in prescriptions"
          :key="prescription.id"
          class="prescription-card"
        >
          <template #content>
            <div class="mb-4">
              <div class="flex justify-between items-start mb-3">
                <div>
                  <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0">
                    Prescription #{{ prescription.id }}
                  </h4>
                  <p class="text-surface-600 dark:text-surface-400">
                    Date: {{ prescription.date }} | Doctor: {{ prescription.doctor }}
                  </p>
                </div>
                <Tag value="Active" severity="success" />
              </div>

              <div class="medications-section">
                <h5 class="text-md font-semibold text-surface-900 dark:text-surface-0 mb-3">
                  Medications
                </h5>
                <div class="space-y-3">
                  <div
                    v-for="(medication, index) in prescription.medications"
                    :key="index"
                    class="medication-item p-3 bg-surface-50 dark:bg-surface-800 rounded-lg"
                  >
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Medicine</label>
                        <p class="text-surface-900 dark:text-surface-0 font-semibold">
                          {{ medication.name }} {{ medication.strength }}
                        </p>
                      </div>
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Frequency</label>
                        <p class="text-surface-900 dark:text-surface-0">{{ medication.frequency }}</p>
                      </div>
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Duration</label>
                        <p class="text-surface-900 dark:text-surface-0">{{ medication.duration }}</p>
                      </div>
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Instructions</label>
                        <p class="text-surface-700 dark:text-surface-300 text-sm">{{ medication.instructions }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="prescription.notes" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <label class="text-sm font-medium text-blue-700 dark:text-blue-300">Doctor's Notes</label>
                <p class="text-blue-800 dark:text-blue-200 text-sm">{{ prescription.notes }}</p>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <Button
            label="Close"
            icon="pi pi-times"
            outlined
            @click="showPrescriptionDialog = false"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
a:hover {
  opacity: 0.8;
}

.medical-record-card,
.prescription-card {
  border-left: 4px solid var(--primary-500);
}

.medications-section {
  border-top: 1px solid var(--surface-border);
  padding-top: 1rem;
}

.medication-item {
  border: 1px solid var(--surface-border);
}

/* Dark mode enhancements */
:global(.p-dark) .medical-history-dialog :deep(.p-dialog),
:global(.p-dark) .prescription-dialog :deep(.p-dialog) {
  background: var(--surface-card);
}
</style>
