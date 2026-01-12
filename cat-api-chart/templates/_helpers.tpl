{{/*
Expand the name of the chart.
*/}}
{{- define "cat-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "cat-api.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cat-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cat-api.labels" -}}
helm.sh/chart: {{ include "cat-api.chart" . }}
{{ include "cat-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "cat-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cat-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: cat-api
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "cat-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cat-api.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database host - use the postgres service name directly
*/}}
{{- define "cat-api.database.host" -}}
postgres-service
{{- end }}

{{/*
Database credentials from secrets
*/}}
{{- define "cat-api.database.username" -}}
{{- .Values.catApi.secrets.postgresql.username }}
{{- end }}

{{- define "cat-api.database.password" -}}
{{- .Values.catApi.secrets.postgresql.password }}
{{- end }}
