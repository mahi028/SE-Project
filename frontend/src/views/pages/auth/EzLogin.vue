<!-- filepath: /home/mahi028/Desktop/SE-Project/frontend/src/views/pages/auth/TokenLogin.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLoginStore } from '@/store/loginStore'
import { useToast } from 'primevue/usetoast'
import { useLazyQuery } from '@vue/apollo-composable';
import gql from 'graphql-tag';

const route = useRoute()
const router = useRouter()
const loginStore = useLoginStore()
const toast = useToast()

const loading = ref(true)
const status = ref('')
const message = ref('')

// GraphQL query to get user data
const GET_USER_DATA = gql`
  query getMe {
    getMe {
      ezId
      name
      email
      role
      profileImageUrl
      senInfo {
        gender
        dob
        address
        pincode
        alternatePhoneNum
        medicalInfo
      }
      docInfo {
        gender
        dob
      }
    }
  }
`;

const { load: fetchUser } = useLazyQuery(GET_USER_DATA);

const processTokenLogin = async () => {
  try {
    const token = route.query.token

    if (!token) {
      throw new Error('No login token provided')
    }

    // Store the token directly in loginStore
    loginStore.setLoginToken(token);

    // Fetch user data to verify token
    const result = await fetchUser(GET_USER_DATA);
    const userData = result?.getMe;

    if (userData) {
      // Set user details in store using existing methods
      loginStore.setLoginDetails(userData);

      // Set role-specific details if available using existing methods
      if (userData.role === 0 && userData.senInfo) {
        loginStore.setSeniorDetails(userData.senInfo);
      } else if (userData.role === 1 && userData.docInfo) {
        loginStore.setDoctorDetails(userData.docInfo);
      }

      status.value = 'success'
      message.value = 'Login successful! Redirecting to your dashboard...'

      toast.add({
        severity: 'success',
        summary: 'Login Successful',
        detail: 'Welcome back to EZCare!',
        life: 3000
      })

      // Redirect based on role and profile completion
      setTimeout(() => {
        const role = userData.role;

        if (role === 0) {
          if (userData.senInfo) {
            router.push({ name: 'Seniordashboard' });
          } else {
            router.push({ name: 'SeniorRegistration' });
          }
        } else if (role === 1) {
          if (userData.docInfo) {
            router.push({ name: 'Doctordashboard' });
          } else {
            router.push({ name: 'DoctorRegistration' });
          }
        } else if (role === 2) {
          router.push({ name: 'ModDashboard' });
        } else {
          router.push('/');
        }
      }, 2000)
    } else {
      throw new Error('Invalid or expired token - no user data received')
    }
  } catch (error) {
    console.error('Token login error:', error);

    status.value = 'error'
    message.value = error.message || 'Login failed. The link may be expired or invalid.'

    toast.add({
      severity: 'error',
      summary: 'Login Failed',
      detail: message.value,
      life: 5000
    })

    // Clear any stored token on error using existing method
    loginStore.clearLoginDetails();

    // Redirect to login page after a delay
    setTimeout(() => {
      router.push('/auth/login')
    }, 3000)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  processTokenLogin()
})
</script>

<template>
  <Toast />
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50 p-4">
    <Card class="w-full max-w-md">
      <template #content>
        <div class="text-center">
          <!-- Loading State -->
          <div v-if="loading" class="py-8">
            <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
            <h3 class="text-xl font-semibold mt-4 mb-2">Processing Login</h3>
            <p class="text-gray-600">Please wait while we verify your login token...</p>
          </div>

          <!-- Success State -->
          <div v-else-if="status === 'success'" class="py-8">
            <div class="text-green-500 mb-4">
              <i class="pi pi-check-circle text-6xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-green-700 mb-2">Login Successful!</h3>
            <p class="text-gray-600 mb-4">{{ message }}</p>
            <ProgressBar mode="indeterminate" class="mb-4" />
            <p class="text-sm text-gray-500">Redirecting to your dashboard...</p>
          </div>

          <!-- Error State -->
          <div v-else class="py-8">
            <div class="text-red-500 mb-4">
              <i class="pi pi-exclamation-triangle text-6xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-red-700 mb-2">Login Failed</h3>
            <p class="text-gray-600 mb-6">{{ message }}</p>

            <div class="space-y-3">
              <Button
                label="Try Again"
                icon="pi pi-refresh"
                severity="secondary"
                outlined
                @click="processTokenLogin"
                class="w-full"
              />
              <Button
                label="Go to Login Page"
                icon="pi pi-sign-in"
                @click="router.push('/auth/login')"
                class="w-full"
              />
            </div>
          </div>

          <!-- EZCare Branding -->
          <div class="mt-8 pt-4 border-t border-gray-200">
            <div class="flex items-center justify-center gap-2 text-green-600">
              <i class="pi pi-heart-fill"></i>
              <span class="font-semibold">EZCare</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">Your Health Companion</p>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
/* Custom styling for the token login page */
.min-h-screen {
  min-height: 100vh;
}

:deep(.p-progressbar) {
  height: 4px;
}

:deep(.p-card) {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}
</style>
