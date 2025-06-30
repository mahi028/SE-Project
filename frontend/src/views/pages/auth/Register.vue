<script setup>
import FloatingConfigurator from '@/components/FloatingConfigurator.vue';
import { Toast } from 'primevue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const formData = ref({
    email: 'abcd@gmail.com  ',
    password: 'abcd',
    confirmPassword: 'abcd',
    role: '',
});

const router = useRouter();

const roles = [
    { label: 'Senior Citizen', value: 'senior' },
    { label: 'Healthcare Professional', value: 'doctor' }
];

const register = () => {
    if (!email.value || !password.value || !confirmPassword.value || !role.value) {
        toast.add({ severity: 'warn', summary: 'Incomplete Form', detail: 'Please fill all the fields.', life: 3000 });
        return;
    }

    if (password.value !== confirmPassword.value) {
        toast.add({ severity: 'error', summary: 'Password Mismatch', detail: 'Passwords do not match.', life: 3000 });
        return;
    }


    const userData = {
        email: email.value,
        role: role.value,
        registered: true
    };

    localStorage.setItem('registeredUser', JSON.stringify(userData));

    alert('Registration successful! Please log in.');
    router.push('/auth/login');
};
</script>

<template>
    <FloatingConfigurator />
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

                        <label class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-4">Select Role</label>
                        <div class="flex flex-col gap-3 md:flex-row md:gap-8 mb-8">
                          <div v-for="r in roles" :key="r.value" class="flex items-center">
                            <RadioButton :inputId="r.value" name="role" :value="r.value" v-model="formData.role" class="mr-2" />
                            <label :for="r.value" class="ml-1">{{ r.label }}</label>
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
