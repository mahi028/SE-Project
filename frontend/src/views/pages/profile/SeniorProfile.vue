<script setup>
import { ref, onMounted } from 'vue'
import { seniorService } from '@/service/SeniorService'
import { useRoute } from 'vue-router'
import InfoItem from '@/components/InfoItem.vue'
import DoctorAppointments from '@/components/doctorDashboard/DoctorAppointments.vue'

const route = useRoute()
const userDetails = ref({})

onMounted(async () => {
  try {
    userDetails.value = await seniorService.getSenior({ "ez_id": route.params.ez_id })
  } catch (error) {
    console.error('Failed to load user data:', error)
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
            <h2 class="text-2xl font-bold mb-3">{{ userDetails.name }}</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <InfoItem type="basic" label="Address" :value="userDetails.address + ', ' + userDetails.pincode" />
              <InfoItem type="basic" label="Contact" :value="userDetails.phone" />
              <InfoItem
                type="basic"
                label="Email"
                :value="userDetails.email"
              />
            </div>
            <div class="mt-2">
              <InfoItem
                type="basic"
                label="Reason for Visit"
                value="Lorem ipsum dolor sit amet consectetur adipisicing elit. Repellat facilis laboriosam ipsam earum unde velit quis quod distinctio aspernatur exercitationem?"
              />
            </div>
          </div>
        </div>
        <Divider />
         <DoctorAppointments />
      </template>
    </Card>
  </div>
</template>

<style scoped>
a:hover {
  opacity: 0.8;
}
</style>
