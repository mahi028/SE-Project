<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue';
import { useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';

const formData = ref({
  email: '',
  password: '',
  confirmPassword: '',
  name: '',
  phoneNum: '',
  role: null,
});

const router = useRouter();
const toast = useToast();

const roles = [
  { label: 'Senior Citizen', value: 0 },
  { label: 'Healthcare Professional', value: 1 }
];

const REGISTER_MUTATION = gql`
  mutation Register(
    $confirmPassword: String!
    $email: String!
    $name: String!
    $password: String!
    $phoneNum: String!
    $role: Int!
  ) {
    register(
      confirmPassword: $confirmPassword
      email: $email
      name: $name
      password: $password
      phoneNum: $phoneNum
      role: $role
    ) {
      message
      status
    }
  }
`;

const { mutate: registerUser, loading, error } = useMutation(REGISTER_MUTATION);

const register = async () => {
  const { isValid, errors } = validateRegistration(formData.value);
  if (!isValid) {
    errors.forEach(err => toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: err,
      life: 3000,
    }));
    return;
  }

  try {
    const variables = {
      email: formData.value.email,
      password: formData.value.password,
      confirmPassword: formData.value.confirmPassword,
      name: formData.value.name,
      phoneNum: formData.value.phoneNum,
      role: Number(formData.value.role),
    };
    const { data } = await registerUser(variables);
    const response = data?.register;

    if (response?.status === 200) {
      toast.add({
        severity: 'success',
        summary: 'Registration Successful',
        detail: response.message || 'You can now log in.',
        life: 3000,
      });
      router.push({ name: 'login' });
    } else {
      toast.add({
        severity: 'error',
        summary: 'Registration Failed',
        detail: `Error: ${response?.message || 'Unknown error'}`,
        life: 3000,
      });
    }
  } catch (err) {
    console.error('Registration error:', error.value || err);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Something went wrong. Please try again.',
      life: 3000,
    });
  }
};

function validateRegistration(form) {
  const errors = [];

  if (!form.name?.trim()) errors.push('Name is required.');
  if (!form.email?.trim()) errors.push('Email is required.');
  if (!form.password) errors.push('Password is required.');
  if (!form.confirmPassword) errors.push('Confirm Password is required.');
  if (!form.phoneNum?.trim()) errors.push('Phone number is required.');
  if (form.role !== 0 && form.role !== 1) errors.push('Role is required.');

  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.push('Invalid email format.');
  }
  if (form.password && form.password.length < 6) {
    errors.push('Password must be at least 6 characters.');
  }
  if (form.password && form.confirmPassword && form.password !== form.confirmPassword) {
    errors.push('Passwords do not match.');
  }
  if (form.phoneNum && !/^\d{10}$/.test(form.phoneNum)) {
    errors.push('Phone number must be exactly 10 digits.');
  }

  return { isValid: errors.length === 0, errors };
}
</script>

<template>
    <FloatingConfigurator />
    <Toast />
    <div class="bg-surface-50 dark:bg-surface-950 flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden">
        <div class="flex flex-col items-center justify-center">
            <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, var(--primary-color) 10%, rgba(33, 150, 243, 0) 30%)">
                <div class="w-full bg-surface-0 dark:bg-surface-900 py-20 px-8 sm:px-20" style="border-radius: 53px">
                    <div class="text-center mb-8">
                        <div class="text-surface-900 dark:text-surface-0 text-3xl font-medium mb-4">Create Account</div>
                        <span class="text-muted-color font-medium">Register to continue</span>
                    </div>

                    <div>
                        <label for="email" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Email</label>
                        <InputText id="email" type="email" placeholder="Email address" class="w-full md:w-[30rem] mb-6" v-model="formData.email" />

                        <label for="password" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Password</label>
                        <Password id="password" v-model="formData.password" placeholder="Password" :toggleMask="true" class="mb-6" fluid :feedback="false" />

                        <label for="confirm" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Confirm Password</label>
                        <Password id="confirm" v-model="formData.confirmPassword" placeholder="Confirm Password" :toggleMask="true" class="mb-6" fluid :feedback="false" />

                        <label for="name" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Full Name</label>
                        <InputText id="name" v-model="formData.name" placeholder="Full Name" :toggleMask="true" class="mb-6" fluid :feedback="false" />

                        <label for="phoneNum" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Phone Number</label>
                        <InputText id="phoneNum" v-model="formData.phoneNum" placeholder="Phone Number" :toggleMask="true" class="mb-6" fluid :feedback="false" />

                        <label class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-4">Select Role</label>
                        <div class="flex flex-col gap-3 md:flex-row md:gap-8 mb-8">
                          <div v-for="r in roles" :key="r.value" class="flex items-center">
                            <RadioButton :inputId="`role-${r.value}`" name="role" :value="r.value" v-model="formData.role" class="mr-2" />
                            <label :for="`role-${r.value}`" class="ml-1">{{ r.label }}</label>
                          </div>
                        </div>

                        <Button label="Register" class="w-full mb-4" @click="register" />
                        <div class="text-center">
                            <span class="text-sm">Already have an account? <router-link to="/auth/login" class="text-primary font-medium">Login</router-link></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.pi-eye {
    transform: scale(1.6);
    margin-right: 1rem;
}

.pi-eye-slash {
    transform: scale(1.6);
    margin-right: 1rem;
}
</style>
