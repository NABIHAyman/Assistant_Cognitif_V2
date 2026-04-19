<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-indigo-600 text-white shadow-md">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold tracking-tight">🧠 Cognition Web</h1>
        <span class="text-indigo-200 text-sm">Powered by Docker Model Runner & Pydantic-AI</span>
      </div>
    </header>

    <main class="flex-grow max-w-7xl mx-auto w-full px-4 py-8">

      <div v-if="!proposal && !isLoading"
           class="border-4 border-dashed border-slate-300 rounded-xl p-20 flex flex-col items-center justify-center text-slate-500 hover:border-indigo-400 hover:bg-indigo-50 transition-colors cursor-pointer"
           @dragover.prevent
           @drop.prevent="handleDrop"
           @click="triggerFileInput">
        <svg class="w-16 h-16 mb-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
        <p class="text-xl font-medium">Glissez votre capture d'écran ici</p>
        <p class="text-sm mt-2">ou cliquez pour parcourir</p>
        <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileSelect">
      </div>

      <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
        <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mb-4"></div>
        <p class="text-lg font-medium text-slate-600 animate-pulse">L'agent IA analyse l'image en local...</p>
      </div>

      <div v-if="proposal && !isLoading" class="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-col">
          <h2 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">Source Visuelle</h2>
          <div class="flex-grow flex items-center justify-center bg-slate-100 rounded-lg overflow-hidden">
            <img :src="previewUrl" alt="Capture à analyser" class="max-w-full max-h-[600px] object-contain">
          </div>
        </div>

        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col space-y-4">

          <div class="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-r-lg">
            <p class="text-sm text-indigo-900"><strong>🧠 Raisonnement de l'IA :</strong> {{ proposal.reasoning }}</p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Titre</label>
              <input v-model="proposal.title" type="text" class="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">
                Domaine
                <span v-if="proposal.is_new_domain" class="ml-2 bg-amber-100 text-amber-800 text-[10px] px-2 py-0.5 rounded-full">NOUVEAU !</span>
              </label>
              <input v-model="proposal.domain" type="text" class="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Action</label>
              <select v-model="proposal.action" class="w-full border border-slate-300 rounded px-3 py-2 outline-none">
                <option value="create">CREATE (Nouveau fichier)</option>
                <option value="append">APPEND (Fichier existant)</option>
                <option value="ignore">IGNORE (Bruit)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Tags consolidés</label>
              <input v-model="mergedTags" type="text" class="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
            </div>
          </div>

          <div v-if="proposal.action === 'append'" class="animate-fade-in">
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Fichier Cible</label>
            <input v-model="proposal.target_file" type="text" class="w-full border border-emerald-300 bg-emerald-50 rounded px-3 py-2 outline-none">
          </div>

          <div class="flex-grow flex flex-col">
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Contenu Markdown</label>
            <textarea v-model="proposal.markdown_content" rows="10" class="w-full flex-grow border border-slate-300 rounded px-3 py-2 font-mono text-sm focus:ring-2 focus:ring-indigo-500 outline-none resize-none"></textarea>
          </div>

          <div class="flex space-x-4 pt-4 border-t border-slate-100">
            <button @click="reject" class="flex-1 bg-white border border-rose-500 text-rose-600 font-bold py-3 rounded-lg hover:bg-rose-50 transition-colors">
              ❌ Rejeter
            </button>
            <button @click="publish" class="flex-1 bg-emerald-500 text-white font-bold py-3 rounded-lg hover:bg-emerald-600 shadow-md hover:shadow-lg transition-all">
              ✅ Approuver & Envoyer (Notion)
            </button>
          </div>

        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const fileInput = ref(null)
const isLoading = ref(false)
const proposal = ref(null)
const previewUrl = ref(null)
const errorMsg = ref(null)

// Fusionner les tags existants et proposés pour l'édition facile
const mergedTags = computed({
  get: () => {
    if (!proposal.value) return ""
    const eTags = proposal.value.existing_tags ? proposal.value.existing_tags.split(',') : []
    const pTags = proposal.value.proposed_new_tags ? proposal.value.proposed_new_tags.split(',') : []
    return [...eTags, ...pTags].filter(t => t.trim() !== '').join(', ')
  },
  set: (val) => {
    // Si l'utilisateur modifie l'input, on stocke tout dans existing_tags pour la soumission
    proposal.value.existing_tags = val
    proposal.value.proposed_new_tags = ""
  }
})

const triggerFileInput = () => fileInput.value.click()

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) processFile(file)
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) processFile(file)
}

const processFile = async (file) => {
  previewUrl.value = URL.createObjectURL(file)
  isLoading.value = true
  errorMsg.value = null

  const formData = new FormData()
  formData.append('file', file)

  try {
    // L'appel part vers /api/analyze (routé vers FastAPI via Vite Proxy ou Nginx)
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (result.status === "success") {
      proposal.value = result.data
    } else if (result.status === "ignored") {
      alert("L'IA a ignoré cette image : " + result.reasoning)
      reset()
    } else {
      throw new Error(result.detail || "Erreur inconnue")
    }
  } catch (error) {
    alert("Erreur de connexion au Backend : " + error.message)
    reset()
  } finally {
    isLoading.value = false
  }
}

const publish = async () => {
  try {
    // On envoie les données modifiées pour écraser celles de l'IA
    const payload = {
      title: proposal.value.title,
      domain: proposal.value.domain,
      action: proposal.value.action,
      target_file: proposal.value.target_file,
      tags: mergedTags.value,
      markdown_content: proposal.value.markdown_content
    }

    const response = await fetch(`/api/publish/${proposal.value.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      alert("🎉 Succès ! Sauvegardé localement et envoyé vers Notion.")
      reset()
    } else {
      alert("Erreur lors de l'approbation.")
    }
  } catch (e) {
    alert("Erreur réseau : " + e.message)
  }
}

const reject = () => {
  // Optionnel : appel API vers /api/reject/{id} pour purger la DB
  fetch(`/api/reject/${proposal.value.id}`, { method: 'POST' })
  reset()
}

const reset = () => {
  proposal.value = null
  previewUrl.value = null
  if (fileInput.value) fileInput.value.value = ""
}
</script>