# VINCULAR OS LEITOS AOS TÉCNICOS E AOS PACIENTES COM OBSERVAÇÕES
# VINCULAR OS MEDICAMENTOS AOS LEITOS

import streamlit as st
import pandas as pd
import datetime
import sqlite3
import time
from medLista_v2 import listaNova



conn = sqlite3.Connection('banco_tecnicas.db', check_same_thread=False)
cursor = conn.cursor()


hora = datetime.datetime.now()
hora_hora = datetime.datetime.now().hour
hora_minuto = datetime.datetime.now().minute
hora_formatada = hora.strftime("%H:%M")

if hora_hora >= 19 and hora_minuto >= 30:
    cursor.execute('DROP TABLE tecnicas')
    cursor.execute('DROP TABLE leitos')
    cursor.execute('DROP TABLE medicamento_administrado')

else:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tecnicas (
                nome_tecnica VARCHAR(100) NOT NULL
                ) 
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leitos (
                numero_leito VARCHAR(5) NOT NULL,
                nome_tecnica VARCHAR(100) NOT NULL
                )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS medicamento_administrado (
                medicamento VARCHAR(150) NOT NULL,
                nome_tecnica VARCHAR(100) NOT NULL,
                numero_leito VARCHAR(5) NOT NULL,
                hora_administracao TIME NOT NULL
                )
    """)

# VERIFICAR SE AS TÉCNICAS ESTÃO NA TABELA, SE NÃO, ADICIONÁ-LAS
cursor.execute('SELECT nome_tecnica FROM tecnicas')
tecnicas_retornadas = cursor.fetchone()
if tecnicas_retornadas is None or tecnicas_retornadas is False:
    lista_tecnicos = ['Marilu Marques', 'Rhaiani Oliveira', 'Ketylin Boff', 'Evelyn Lemos', 'Vitória Bulmini', 'Francieli Bettin', 'Ivanice Juliana', 'Daniel Miguel', 'Camila Vasconcellos', 'Juliana Marcilio', 'Luisa Cardoso', 'Greice Porto']

    for tec in lista_tecnicos:
        cursor.execute('INSERT INTO tecnicas (nome_tecnica) VALUES (?)', (tec, ))
        conn.commit()
    st.toast('Inserindo técnicas...')

# VERIFICAR SE OS LEITOS ESTÃO NA TABELA, SE NÃO, ADICIONÁ-LOS
cursor.execute('SELECT numero_leito FROM leitos')
leitos_ret = cursor.fetchone()
if leitos_ret is None or leitos_ret is False:
    lista_leitos = ['400A', '400B', '401A', '401B', '402A', '402B', '403A', '403B', '404A', '404B', '405A', '405B', '406A', '406B', '407A', '407B', '408A', '408B', '409A', '409B', '410A', '410B', '411A', '411B', '412A', '412B', '413A', '413B', '414A', '414B', '415A', '415B', '416A', '416B', '417A', '417B', '418A', '418B', '419A', '419B', '420A', '420B', '421P', '422P', '423P', '424P', '425P', '426P', '427P', '428P', '429P', '430P']
    
    for le in lista_leitos:
        cursor.execute("INSERT INTO leitos (numero_leito, nome_tecnica) VALUES (?, '0')", (le,))
        conn.commit()
    st.toast('Inserindo leitos...')

#* ADICIONAR TÉCNICOS E LEITOS
menu = st.sidebar.selectbox("Menu", ("Resumo", "Administrar medicamento", "Histórico", "Transferir/excluir leito (alta)", "Recusa", "Vincular técnica"))

lista_tecnicos = ['Marilu Marques', 'Rhaiani Oliveira', 'Ketylin Boff', 'Evelyn Lemos', 'Vitória Bulmini', 'Francieli Bettin', 'Ivanice Juliana', 'Daniel Miguel', 'Camila Vasconcellos', 'Juliana Marcilio', 'Luisa Cardoso', 'Greice Porto', 'Outro']

lista_leitos = ['400A', '400B', '401A', '401B', '402A', '402B', '403A', '403B', '404A', '404B', '405A', '405B', '406A', '406B', '407A', '407B', '408A', '408B', '409A', '409B', '410A', '410B', '411A', '411B', '412A', '412B', '413A', '413B', '414A', '414B', '415A', '415B', '416A', '416B', '417A', '417B', '418A', '418B', '419A', '419B', '420A', '420B', '421P', '422P', '423P', '424P', '425P', '426P', '427P', '428P', '429P', '430P']

lista_medicamentos = {med["nome"]: id for id, med in listaNova.items()}


if menu == "Vincular técnica":
    # buscar lista de leitos ainda não vinculados
    cursor.execute("SELECT numero_leito FROM leitos WHERE nome_tecnica = '0'")
    lista_numero_leito = cursor.fetchall()

    leitos_livres = []
    for nleito in lista_numero_leito:
        leitos_livres.append(*nleito)

    tecnica = st.selectbox('Selecione a técnica', options=lista_tecnicos, index=None, placeholder="")
    if tecnica == 'Outro':
        tecnica = st.text_input('Insira o nome da técnica')
    leito = st.multiselect('Selecione os leitos', options=leitos_livres, placeholder="")

    leito_selecionados = ', '.join(leito)

    vincular_btn = st.button('Vincular', type="primary")
    if vincular_btn:
        for i in leito:
            cursor.execute("UPDATE leitos SET nome_tecnica = ? WHERE numero_leito = ?", (tecnica, i))
            conn.commit()
        
        st.info(f'Leitos **{leito_selecionados}** adicionados para a técnica **{tecnica}**.')

elif menu == "Administrar medicamento":
    cursor.execute("SELECT DISTINCT nome_tecnica FROM leitos WHERE nome_tecnica <> '0'")
    lista_tecnicas_com_leito_retorno = cursor.fetchall()

    lista_tecnicas_com_leito = []

    for tl in lista_tecnicas_com_leito_retorno:
        lista_tecnicas_com_leito.append(*tl)

    tecnico_administrar = st.selectbox('Selecione a técnica para administrar', options=lista_tecnicas_com_leito, index=None, placeholder="")
    if tecnico_administrar is not None:
        cursor.execute('SELECT numero_leito FROM leitos WHERE nome_tecnica = ?', (tecnico_administrar, ))
        leitos_retornados_medicamento = cursor.fetchall()

        leito_vinculado = []

        for lei in leitos_retornados_medicamento:
            leito_vinculado.append(*lei)

        medicamento_administrar = st.selectbox('Selecione o medicamento', options=lista_medicamentos, index=None, placeholder="")
        leito_administrar = st.selectbox('Selecione o leito', options=leito_vinculado, index=None, placeholder="")
    
        if medicamento_administrar is not None and leito_administrar is not None:
            cursor.execute('SELECT medicamento, numero_leito, hora_administracao FROM medicamento_administrado WHERE medicamento = ? AND numero_leito = ? ORDER BY hora_administracao DESC', (medicamento_administrar, leito_administrar))
            retorno_checar_hora = cursor.fetchone()


            if retorno_checar_hora is not None:
                medicamento_administrar_retorno = retorno_checar_hora[0]
                leito_administrar_retorno = retorno_checar_hora[1]
                hora_retorno = retorno_checar_hora[2]

                formato_horas = '%H:%M'
                hora_banco = datetime.datetime.strptime(hora_retorno, formato_horas)
                hora_atual = datetime.datetime.strptime(hora_formatada, formato_horas)

                diferenca_horas = hora_atual - hora_banco
                if diferenca_horas.total_seconds() < 3600:
                    st.info(f':warning: O medicamento **{medicamento_administrar_retorno}** foi administrado no paciente do leito **{leito_administrar_retorno}** às **{hora_retorno}**, **há menos de uma hora**. Você tem certeza que quer administrar novamente?')

    outra_administrando_checar = st.checkbox('Outra técnica está administrando pela técnica responsável pelo leito.')
    if outra_administrando_checar:
        outra_tecnica = st.selectbox("Selecione a técnica auxiliar", options=lista_tecnicos, index=None, placeholder="")

        if outra_tecnica == "Outro":
            outra_tecnica = st.text_input('Insira o nome da técnica')

    checar_btn = st.button('Administrar', type="primary")
    if checar_btn:
        if outra_administrando_checar is False:
            try:
                cursor.execute('INSERT INTO medicamento_administrado (medicamento, nome_tecnica, numero_leito, hora_administracao) VALUES (?, ?, ?, ?)', (medicamento_administrar, tecnico_administrar, leito_administrar, hora_formatada))
                conn.commit()
                
                time.sleep(1)
                st.success(':pill: Medicamento administrado com sucesso!')
            
            except Exception as e:
                st.error(f"Erro: {e}")
        else:
            try:
                cursor.execute('INSERT INTO medicamento_administrado (medicamento, nome_tecnica, numero_leito, hora_administracao) VALUES (?, ?, ?, ?)', (medicamento_administrar, outra_tecnica, leito_administrar, hora_formatada))
                conn.commit()

                time.sleep(1)
                st.success(':pill: Medicamento administrado com sucesso!')
            
            except Exception as e:
                st.error(f"Erro: {e}")

elif menu == "Histórico":
    cursor.execute('SELECT nome_tecnica, medicamento, numero_leito, hora_administracao FROM medicamento_administrado ORDER BY hora_administracao DESC')
    historico_retornado = cursor.fetchall()

    nome_tecnica_historico = []
    medicamento_historico = []
    numero_leito_historico = []
    hora_historico = []

    for sublista in historico_retornado:
        nome_tecnica_iterado = sublista[0]
        medicamento_iterado = sublista[1]
        numero_leito_iterado = sublista[2]
        hora_iterado = sublista[3]

        nome_tecnica_historico.append(nome_tecnica_iterado)
        medicamento_historico.append(medicamento_iterado)
        numero_leito_historico.append(numero_leito_iterado)
        hora_historico.append(hora_iterado)

    for h in range(len(nome_tecnica_historico)):
        nome_tecnica_apresentar = nome_tecnica_historico[h]
        medicamento_apresentar = medicamento_historico[h]
        numero_leito_apresentar = numero_leito_historico[h]
        hora_apresentar = hora_historico[h]

        st.info(f"A técnica **{nome_tecnica_apresentar}** administrou **{medicamento_apresentar}** no leito **{numero_leito_apresentar}** às **{hora_apresentar}**.")

elif menu == "Transferir/excluir leito (alta)":
    # CONSULTAR LEITOS OCUPADOS
    cursor.execute("SELECT numero_leito FROM leitos WHERE nome_tecnica <> '0'")
    leitos_desvincular_retorno = cursor.fetchall()

    leitos_para_desvincular = []

    for leitos_desv in leitos_desvincular_retorno:
        leitos_para_desvincular.append(*leitos_desv)

    st.subheader('Desvincular leito')
    st.caption('Para o caso onde o paciente recebe alta ou é transferido para outro andar. O leito será desvinculado da técnica atual.')
    leito_excluir = st.selectbox("Selecione o leito para desvincular", options=leitos_para_desvincular, index=None, placeholder="")
    confirmar_leito_excluir = st.checkbox('Confirmo o desvínculo do leito selecionado.')

    desvincular_btn = st.button('Desvincular', type="primary")
    if desvincular_btn:
        if confirmar_leito_excluir is False:
            st.error('Por favor, confirme que deseja desvincular o leito.')
        else:
            cursor.execute("UPDATE leitos SET nome_tecnica = '0' WHERE numero_leito = ?", (leito_excluir, ))
            conn.commit()

            cursor.execute("DELETE FROM medicamento_administrado WHERE numero_leito = ?", (leito_excluir, ))
            conn.commit()

            time.sleep(2)
            st.success('Leito desvinculado com sucesso! :thumbsup:')

    st.divider()
    st.subheader('Transferir paciente')
    st.caption('Transferir o paciente/leito para outra técnica do 4º andar.')
    leito_transferir = st.selectbox('Selecione o leito para transferir', options=leitos_para_desvincular, index=None, placeholder="")
    tecnica_transferir = st.selectbox('Selecione a técnica que vai receber este leito', options=lista_tecnicos, index=None, placeholder="")

    if tecnica_transferir == "Outro":
        tecnica_transferir = st.text_input('Insira o nome da técnica que vai receber este leito')

    confirmar_transferencia = st.checkbox('Confirmo a transferência de leito.')

    confirmar_transferencia_btn = st.button('Transferir', type="primary")
    if confirmar_transferencia_btn:
        if confirmar_transferencia is False:
            st.error('Por favor, confirme a transferência de leito.')
        else:
            cursor.execute('UPDATE leitos SET nome_tecnica = ? WHERE numero_leito = ?', (tecnica_transferir, leito_transferir))
            conn.commit()

            time.sleep(2)
            st.success(f'Leito **{leito_transferir}** transferido com sucesso para a(o) técnica(o) **{tecnica_transferir}**!')

elif menu == "Recusa":
    cursor.execute("SELECT numero_leito FROM medicamento_administrado ORDER BY numero_leito ASC")
    leitos_recusa_retorno = cursor.fetchall()

    lista_leitos_recusa = []

    for lr in leitos_recusa_retorno:
        lista_leitos_recusa.append(*lr)


    leito_recusa = st.selectbox('Selecione o leito da recusa', options=lista_leitos_recusa, index=None, placeholder="")
    if leito_recusa is not None:
        cursor.execute('SELECT medicamento, numero_leito, hora_administracao FROM medicamento_administrado WHERE numero_leito = ? ORDER BY hora_administracao DESC', (leito_recusa, ))
        leito_recusa_retornado = cursor.fetchall()

        opcoes = [f"{medicamento_r} | {leito_r} | {hora_r}" for medicamento_r, leito_r, hora_r in leito_recusa_retornado]
        horarios = [hora_r for medicamento_r, leito_r, hora_r in leito_recusa_retornado]
        leito_horario = [f"{leito_r} | {hora_r}" for medicamento_r, leito_r, hora_r in leito_recusa_retornado]

        selecionado_recusa = st.radio("Selecione o medicamento para recusa: ", options=opcoes, captions=leito_horario)

        indice_selecionado = opcoes.index(selecionado_recusa)
        hora_selecionada = horarios[indice_selecionado]

        medicamento_selecionado_recusa, leito_selecionado_recusa, hora_selecionada_recusa = selecionado_recusa.split(' | ')

        st.divider()

        confirmar_recusa = st.checkbox('Confirmo a recusa do medicamento.')

        recusa_btn = st.button('Recusar medicamento', type="primary")
        if recusa_btn:
            if confirmar_recusa is False:
                st.error('Por favor, confirme a recusa do medicamento.')
            else:
                try:
                    cursor.execute('DELETE FROM medicamento_administrado WHERE numero_leito = ? AND medicamento = ? AND hora_administracao = ?', (leito_selecionado_recusa, medicamento_selecionado_recusa, hora_selecionada_recusa))
                    conn.commit()

                    time.sleep(1)
                    st.success('Medicamento recusado com sucesso!')
                except Exception as e:
                    st.error(f"Erro: {e}")

elif menu == "Resumo":
    cursor.execute("SELECT nome_tecnica, numero_leito FROM leitos WHERE nome_tecnica <> '0'")
    resumo_retorno = cursor.fetchall()

    if len(resumo_retorno) != 0:
        tecnicas_resumo = {}

        for resumo_tec, resumo_lei in resumo_retorno:
            if resumo_tec not in tecnicas_resumo:
                tecnicas_resumo[resumo_tec] = []
            tecnicas_resumo[resumo_tec].append(resumo_lei)

        def create_card(resumo_tec, leitos):
            leitos_html = ' '.join([f'<span>{le}</span>' for le in leitos])

            card_html = f"""
            <div style='display: flex; flex-direction: column; justify-content: center; align-items: center;'>
                <div style='display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 16px; padding: 16px; width: 400px; border-bottom: 4px solid; background: linear-gradient(to bottom, #00A344, #003D1A)'>
                    <h3 style="text-align: center; font-size: 2rem;">{resumo_tec}</h3>
                    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px; font-size: 1.3rem;">{leitos_html}</div>
                </div>
            </div>
            """
            return card_html
        
        for resumo_tec, leitos in tecnicas_resumo.items():
            st.markdown(create_card(resumo_tec, leitos), unsafe_allow_html=True)
    else:
        st.subheader('Não há técnicas com leitos vinculados.')
        st.markdown('Por favor, vincule os leitos na aba :blue[Vincular técnica].')