<script setup>
    import { ref } from 'vue';
    import { RouterLink } from 'vue-router';

    const props = defineProps({
        page: String,
    })

    const doctorWidgets = ref([
        {
            id: 1,
            label: 'Patient Lookup',
            desc: 'Find Patients info from email or just their face.',
            iconClass: 'pi pi-camera text-blue-500 !text-xl',
            redirect: '#'
        },
    ])

    const seniorWidgets = ref([
        {
            id: 1,
            label: '1st ',
            desc: 'lorem ipsum dolar sit emmet.',
            iconClass: 'pi pi-camera text-blue-500 !text-xl',
            redirect: '#',
        },
        {
            id: 2,
            label: '2nd',
            desc: 'lorem ipsum dolar sit emmet.',
            iconClass: 'pi pi-camera text-blue-500 !text-xl',
            redirect: '#',
        },
    ])
</script>
<template>
    <div class="col-span-12 lg:col-span-6 xl:col-span-3" v-for="widget in props.page == 'doctor' ? doctorWidgets : seniorWidgets" key="id">
        <RouterLink :to="widget.redirect">
            <div class="card mb-0">
                <div class="flex justify-between mb-4">
                    <div>
                        <span class="block text-muted-color font-medium mb-4">{{ widget.label }}</span>
                    </div>
                    <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                        <i :class="widget.iconClass"></i>
                    </div>
                </div>
                <span class="text-muted-color">{{ widget.desc }}</span>
            </div>
        </RouterLink>
    </div>
</template>
