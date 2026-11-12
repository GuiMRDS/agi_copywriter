'use client'
import { useRef, useState } from 'react'
import { toast } from 'sonner'
import { Paperclip, X } from 'lucide-react'
import { TextArea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useQueryState } from 'nuqs'
import Icon from '@/components/ui/icon'

const ChatInput = () => {
  const { chatInputRef } = useStore()

  const { handleStreamResponse } = useAIChatStreamHandler()
  const [selectedAgent] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [inputMessage, setInputMessage] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const isStreaming = useStore((state) => state.isStreaming)
  const handleSubmit = async () => {
    if (!inputMessage.trim()) return

    const formData = new FormData()
    formData.append('message', inputMessage)
    files.forEach((file) => formData.append('files', file))
    setInputMessage('')
    setFiles([])

    try {
      await handleStreamResponse(formData)
    } catch (error) {
      toast.error(
        `Error in handleSubmit: ${
          error instanceof Error ? error.message : String(error)
        }`
      )
    }
  }

  return (
    <div className="relative mx-auto mb-1 flex w-full max-w-2xl flex-col gap-y-2 font-geist">
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {files.map((file, i) => (
            <span
              key={`${file.name}-${i}`}
              className="flex items-center gap-1 rounded-lg border border-accent bg-primaryAccent px-2 py-1 text-xs text-primary"
            >
              {file.name}
              <button
                onClick={() => setFiles(files.filter((_, j) => j !== i))}
                aria-label={`Remover ${file.name}`}
              >
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
      )}
      <div className="flex w-full items-end justify-center gap-x-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          multiple
          hidden
          onChange={(e) => {
            setFiles([...files, ...Array.from(e.target.files ?? [])])
            e.target.value = ''
          }}
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={!(selectedAgent || teamId) || isStreaming}
          size="icon"
          variant="ghost"
          className="rounded-xl p-5 text-primary"
          aria-label="Anexar vídeo"
        >
          <Paperclip size={18} />
        </Button>
        <TextArea
          placeholder={'Ask anything'}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => {
            if (
              e.key === 'Enter' &&
              !e.nativeEvent.isComposing &&
              !e.shiftKey &&
              !isStreaming
            ) {
              e.preventDefault()
              handleSubmit()
            }
          }}
          className="w-full border border-accent bg-primaryAccent px-4 text-sm text-primary focus:border-accent"
          disabled={!(selectedAgent || teamId)}
          ref={chatInputRef}
        />
        <Button
          onClick={handleSubmit}
          disabled={
            !(selectedAgent || teamId) || !inputMessage.trim() || isStreaming
          }
          size="icon"
          className="rounded-xl bg-primary p-5 text-primaryAccent"
        >
          <Icon type="send" color="primaryAccent" />
        </Button>
      </div>
    </div>
  )
}

export default ChatInput
