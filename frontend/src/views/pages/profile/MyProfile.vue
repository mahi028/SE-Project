<script setup>
import { ref, onMounted } from 'vue'
import { useLoginStore } from '@/store/loginStore'
import { seniorService } from '@/service/SeniorService'
import { doctorService } from '@/service/DoctorService'
import InfoItem from '@/components/InfoItem.vue'

const loginStore = useLoginStore()
const ez_id = loginStore.ez_id
const role = loginStore.role
const userDetails = ref({})

onMounted(async () => {
  try {
    if (role === 'doctor') {
      userDetails.value = await doctorService.getDoctor({ ez_id })
    } else if (role === 'senior') {
      userDetails.value = await seniorService.getSenior({ ez_id })
    }
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
})
</script>

<template>
  <div class="p-4 max-w-6xl mx-auto">
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
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" v-if="userDetails.role === 'doctor'">
              <InfoItem type="basic" label="Location" :value="userDetails.address + ', ' + userDetails.pincode" />
              <InfoItem type="basic" label="Specialization" :value="userDetails.specialization || 'N/A'" />
              <div>
                <span class="text-lg font-semibold block mb-1">Reviews</span>
                <Rating :modelValue="parseInt(userDetails.reviews || 0)" readonly :cancel="false" />
              </div>
              <InfoItem
                type="basic"
                label="Contact"
                :value="userDetails.phone"
                :isLink="true"
                :href="`tel:${userDetails.phone}`"
              />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" v-else-if="userDetails.role === 'senior'">
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

        <!-- Professional & Affiliation Info for Doctors -->
        <div v-if="userDetails.role === 'doctor'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Professional Info -->
          <div>
            <h3 class="text-xl font-semibold mb-3">Professional Information</h3>
            <InfoItem label="Specialization" :value="userDetails.specialization" />
            <InfoItem label="Years of Experience" :value="userDetails.experience" />
            <InfoItem label="Degrees/Qualifications" :value="userDetails.qualification" />
          </div>

          <!-- Affiliation Info -->
          <div>
            <h3 class="text-xl font-semibold mb-3">Affiliation & Work Details</h3>
            <InfoItem label="Hospital/Clinic" :value="userDetails.hospital" />
            <InfoItem
              label="Official Email"
              :value="userDetails.email"
              :isLink="true"
              :href="`mailto:${userDetails.email}`"
            />
            <InfoItem label="Working Hours" :value="userDetails.timings" />
            <InfoItem
              label="Days Available"
              :value="(userDetails.availability || []).join(', ')"
            />
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
