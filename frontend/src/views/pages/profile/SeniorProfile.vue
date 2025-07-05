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

const route = useRoute()
const loginStore = useLoginStore()
const userDetails = ref({})
const appointments = ref([])
const vitals = ref([])
const loading = ref(false)

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
</script>

<template>
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
              <Column field="date" header="Date" sortable style="width: 25%">
                <template #body="{ data }">
                  <span class="font-semibold text-base">{{ data.date }}</span>
                </template>
              </Column>
              <Column field="time" header="Time" style="width: 20%">
                <template #body="{ data }">
                  <span class="text-base">{{ data.time }}</span>
                </template>
              </Column>
              <Column field="reason" header="Reason" style="width: 55%">
                <template #body="{ data }">
                  <span class="text-base">{{ data.reason }}</span>
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
  </div>
</template>

<style scoped>
a:hover {
  opacity: 0.8;
}
</style>
